#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReAct Agent - Reasoning + Acting Pattern

A simple ReAct agent implementation using Google Gemini.
Based on the pattern from DeepLearning.AI's LangGraph course.

The agent follows: Thought → Action → Pause → Observation → Answer
"""

import os
import re
import sys
import time
from typing import Dict, Callable

import docker
from google import genai
from google.genai import types


# System prompt that teaches the agent the ReAct pattern
SYSTEM_PROMPT = """You are a helpful AI assistant that uses tools to answer questions.

You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.

Use Thought to describe what you're thinking about the question.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 + 7
Adds two numbers together

wait:
e.g. wait: please wait
Waits for 5 seconds

count_test:
e.g. count_test: run the counter
Runs a counting test from 1 to 10 in a Docker container with real-time streaming output

Example session:

Question: What is 10 + 25?
Thought: I need to add two numbers: 10 and 25.
Action: calculate: 10 + 25
PAUSE

You will be called again with this:

Observation: 35

You then output:

Answer: The result of 10 + 25 is 35.

IMPORTANT RULES:
1. Always follow the format: Thought, Action, PAUSE (then wait for Observation)
2. After receiving Observation, provide your Answer
3. Only use actions that are available to you
4. Be concise in your thoughts
5. The Action line should be in format "Action: tool_name: input"
""".strip()


class Agent:
    """ReAct Agent that uses Gemini for reasoning and tool execution"""

    def __init__(self, system_message: str, api_key: str, model_name: str = "gemini-flash-latest"):
        """Initialize the agent"""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.system_message = system_message
        self.messages = []

        # Add system message to conversation
        if system_message:
            self.messages.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=f"System instructions:\n{system_message}")]
                )
            )
            # Add acknowledgment from model
            self.messages.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text="I understand. I will follow the ReAct pattern: Thought → Action → PAUSE → Observation → Answer.")]
                )
            )

    def __call__(self, message: str) -> str:
        """Send a message and get a response"""
        # Add user message
        self.messages.append(
            types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
        )

        # Execute and get response
        result = self.execute()

        # Add assistant response
        self.messages.append(
            types.Content(
                role="model",
                parts=[types.Part(text=result)]
            )
        )

        return result

    def execute(self) -> str:
        """Execute the current conversation with Gemini"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=self.messages,
            config=types.GenerateContentConfig(
                temperature=0,  # Deterministic responses
                max_output_tokens=1024,
            )
        )

        return response.text if hasattr(response, 'text') else ""


# Tool Functions
def calculate(expression: str) -> str:
    """
    Add two numbers together

    Args:
        expression: A string like "4 + 7" or "10 + 25"

    Returns:
        The result as a string
    """
    try:
        # Parse the expression (expecting format "number + number")
        parts = expression.strip().split('+')
        if len(parts) != 2:
            return "Error: Please provide expression in format 'number + number'"

        num1 = float(parts[0].strip())
        num2 = float(parts[1].strip())
        result = num1 + num2

        # Return as integer if it's a whole number
        if result.is_integer():
            return str(int(result))
        return str(result)

    except (ValueError, AttributeError) as e:
        return f"Error: Could not parse numbers from '{expression}'"


def wait(input_text: str) -> str:
    """
    Wait for 5 seconds

    Args:
        input_text: Any input text (ignored, just for consistency)

    Returns:
        A message indicating the wait is complete
    """
    time.sleep(5)
    return "Waited for 5 seconds"


def count_test(input_text: str) -> str:
    """
    Run a counting test from 1 to 10 in a Docker container with streaming output
    Returns after 4 seconds with whatever content has been streamed so far

    Args:
        input_text: Any input text (ignored, just for consistency)

    Returns:
        The output collected within 4 seconds
    """
    try:
        # Connect to Docker
        client = docker.from_env()

        # Try to find a running container
        # First, try to find a container with 'substrate' or 'playwright' in the name
        containers = client.containers.list()

        if not containers:
            return "Error: No running Docker containers found"

        # Use the first running container (you can modify this logic to select a specific container)
        container = containers[0]

        print(f"\n  → Using container: {container.name} ({container.id[:12]})")
        print(f"  → Starting count test with streaming output (4 second timeout)...\n")

        # Execute the counting command with streaming
        command = "python -c \"import time; [print(f'Count: {i}', flush=True) or time.sleep(1) for i in range(1, 11)]\""

        exec_result = container.exec_run(
            command,
            stream=True,
            demux=False
        )

        # Collect and print output as it streams, but only for 4 seconds
        output_lines = []
        start_time = time.time()
        timeout = 4.0  # 4 seconds

        for chunk in exec_result.output:
            # Check if we've exceeded the timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                print(f"\n  → Timeout reached after {elapsed:.1f} seconds, returning partial output\n")
                break

            line = chunk.decode('utf-8').strip()
            if line:
                print(f"  {line}")
                output_lines.append(line)

        complete_output = "\n".join(output_lines)

        if time.time() - start_time >= timeout:
            return f"Count test partial output (stopped after 4 seconds):\n{complete_output}"
        else:
            return f"Count test completed. Output:\n{complete_output}"

    except docker.errors.DockerException as e:
        return f"Error connecting to Docker: {str(e)}"
    except Exception as e:
        return f"Error running count test: {str(e)}"


# Available tools
TOOLS: Dict[str, Callable] = {
    "calculate": calculate,
    "wait": wait,
    "count_test": count_test,
}


def query(question: str, api_key: str, max_turns: int = 10, verbose: bool = True) -> str:
    """
    Run a ReAct agent query

    Args:
        question: The question to ask the agent
        api_key: Google API key
        max_turns: Maximum number of reasoning iterations
        verbose: Whether to print intermediate steps

    Returns:
        The final answer
    """
    # Create agent with system prompt
    agent = Agent(SYSTEM_PROMPT, api_key)

    next_prompt = question
    counter = 0

    if verbose:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")

    while counter < max_turns:
        counter += 1

        # Get agent's response
        result = agent(next_prompt)

        if verbose:
            print(f"Turn {counter}:")
            print(result)
            print()

        # Check if we have an answer (agent is done)
        if "Answer:" in result:
            # Extract and return the answer
            answer_match = re.search(r"Answer:\s*(.+)", result, re.DOTALL)
            if answer_match:
                answer = answer_match.group(1).strip()
                if verbose:
                    print(f"{'='*60}")
                    print(f"Final Answer: {answer}")
                    print(f"{'='*60}\n")
                return answer
            return result

        # Look for actions to execute
        # Pattern: "Action: tool_name: input"
        action_pattern = r"Action:\s*(\w+):\s*(.+?)(?:\n|$)"
        action_match = re.search(action_pattern, result)

        if action_match:
            action_name = action_match.group(1).strip()
            action_input = action_match.group(2).strip()

            if verbose:
                print(f"  → Executing: {action_name}({action_input})")

            # Execute the action
            if action_name not in TOOLS:
                error_msg = f"Error: Unknown action '{action_name}'. Available: {list(TOOLS.keys())}"
                if verbose:
                    print(f"  ✗ {error_msg}\n")
                next_prompt = f"Observation: {error_msg}"
            else:
                observation = TOOLS[action_name](action_input)
                if verbose:
                    print(f"  ✓ Observation: {observation}\n")
                next_prompt = f"Observation: {observation}"
        else:
            # No action found and no answer - agent might be confused
            if "PAUSE" in result:
                next_prompt = "Observation: No action was specified. Please specify an action."
            else:
                # Agent might have finished without proper format
                return result

    return "Error: Maximum turns reached without getting an answer"


def main():
    """Main function to run the ReAct agent"""

    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("\n❌ Error: GOOGLE_API_KEY environment variable not set")
        print("\nPlease set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'\n")
        sys.exit(1)

    print("\n" + "="*60)
    print("ReAct Agent - Reasoning + Acting Pattern")
    print("Using Google Gemini")
    print("="*60)

    # Example queries
    examples = [
        "What is 15 + 27?",
        "What is 100 + 250?",
        "Calculate 42 + 58",
    ]

    if len(sys.argv) > 1:
        # Use question from command line
        question = " ".join(sys.argv[1:])
        answer = query(question, api_key, verbose=True)
    else:
        # Run examples
        print("\nRunning example queries...\n")
        for question in examples:
            answer = query(question, api_key, verbose=True)
            input("Press Enter to continue to next example...")

    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()
