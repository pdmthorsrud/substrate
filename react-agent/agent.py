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
Runs a counting test from 1 to 30 in a Docker container with real-time streaming output.
For long-running tasks, you will receive periodic checkpoint updates every 3 seconds.
At each checkpoint, you'll see the partial output and must decide to 'continue' or 'stop'.
Respond with just the word 'continue' if the task should keep running, or 'stop' to terminate it early.

browser_automation:
e.g. browser_automation: Go to nrk.no and find the weather forecast
Controls a web browser via Gemini Computer Use running in a Docker container.
Can navigate websites, click elements, fill forms, extract information, take screenshots, etc.
Executes inside a playwright-browser container with streaming output and 3-second checkpoints.
At each checkpoint, you'll see partial output and must decide to 'continue' or 'stop'.
Use this when you need to interact with websites or gather information from the web.

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


def count_test(input_text: str, agent=None) -> str:
    """
    Run a counting test from 1 to 30 in a Docker container with streaming output
    Uses periodic checkpoints every 3 seconds to ask the agent if it should continue

    Args:
        input_text: Any input text (ignored, just for consistency)
        agent: Optional Agent instance for checkpoint interactions

    Returns:
        The output collected (either complete or stopped by agent decision)
    """
    try:
        # Connect to Docker
        client = docker.from_env()

        # Try to find a running container
        containers = client.containers.list()

        if not containers:
            return "Error: No running Docker containers found"

        # Use the first running container
        container = containers[0]

        print(f"\n  → Using container: {container.name} ({container.id[:12]})")
        print(f"  → Starting count test with streaming output and 3-second checkpoints...\n")

        # Execute the counting command with streaming (count to 30)
        command = "python -c \"import time; [print(f'Count: {i}', flush=True) or time.sleep(1) for i in range(1, 31)]\""

        exec_result = container.exec_run(
            command,
            stream=True,
            demux=False
        )

        # Collect and print output as it streams with periodic checkpoints
        output_lines = []
        start_time = time.time()
        last_checkpoint_time = start_time
        checkpoint_interval = 3.0  # 3 seconds
        checkpoint_count = 0

        for chunk in exec_result.output:
            current_time = time.time()

            # Decode and collect the output
            line = chunk.decode('utf-8').strip()
            if line:
                print(f"  {line}")
                output_lines.append(line)

            # Check if it's time for a checkpoint
            elapsed_since_checkpoint = current_time - last_checkpoint_time
            if agent and elapsed_since_checkpoint >= checkpoint_interval:
                checkpoint_count += 1
                elapsed_total = current_time - start_time

                # Prepare checkpoint message
                current_output = "\n".join(output_lines)
                checkpoint_msg = f"\n{'='*60}\n"
                checkpoint_msg += f"CHECKPOINT #{checkpoint_count} (at {elapsed_total:.1f}s)\n"
                checkpoint_msg += f"{'='*60}\n"
                checkpoint_msg += f"Partial output so far:\n{current_output}\n"
                checkpoint_msg += f"{'='*60}\n"

                print(checkpoint_msg)

                # Add checkpoint to conversation history and ask agent
                observation_prompt = f"Observation: Task is still running (checkpoint #{checkpoint_count} at {elapsed_total:.1f}s). Output so far:\n{current_output}\n\nBased on the output so far, should I continue waiting or stop the task? Respond with just 'continue' or 'stop'."

                # Call agent with checkpoint
                response = agent(observation_prompt)

                print(f"\n  → Agent response: {response}\n")

                # Check if agent wants to stop
                if "stop" in response.lower() and "continue" not in response.lower():
                    print(f"\n  → Agent requested stop at {elapsed_total:.1f}s\n")
                    complete_output = "\n".join(output_lines)
                    return f"Count test stopped by agent decision at checkpoint #{checkpoint_count} ({elapsed_total:.1f}s):\n{complete_output}"

                # Update checkpoint time
                last_checkpoint_time = current_time

        # Task completed naturally
        complete_output = "\n".join(output_lines)
        elapsed_total = time.time() - start_time
        print(f"\n  → Count test completed naturally after {elapsed_total:.1f}s\n")
        return f"Count test completed successfully (took {elapsed_total:.1f}s):\n{complete_output}"

    except docker.errors.DockerException as e:
        return f"Error connecting to Docker: {str(e)}"
    except Exception as e:
        return f"Error running count test: {str(e)}"


def browser_automation(instruction: str, agent=None) -> str:
    """
    Control a web browser via Gemini Computer Use running in a Docker container
    Uses periodic checkpoints every 3 seconds to ask the agent if it should continue

    Args:
        instruction: What the browser should do (e.g., "Go to nrk.no and find the weather")
        agent: Optional Agent instance for checkpoint interactions

    Returns:
        The output from the browser automation task
    """
    try:
        # Connect to Docker
        client = docker.from_env()

        # Find the playwright-browser container
        containers = client.containers.list()

        playwright_container = None
        for container in containers:
            if 'playwright' in container.name.lower() or 'browser' in container.name.lower():
                playwright_container = container
                break

        if not playwright_container:
            return "Error: No playwright-browser container found. Please ensure the container is running."

        print(f"\n  → Using container: {playwright_container.name} ({playwright_container.id[:12]})")
        print(f"  → Starting browser automation with 3-second checkpoints...")
        print(f"  → Instruction: {instruction}\n")

        # Execute gemini_computer_use.py with the instruction
        command = f'python /app/gemini_computer_use.py "{instruction}"'

        exec_result = playwright_container.exec_run(
            command,
            stream=True,
            demux=False
        )

        # Collect and print output as it streams with periodic checkpoints
        output_lines = []
        start_time = time.time()
        last_checkpoint_time = start_time
        checkpoint_interval = 3.0  # 3 seconds
        checkpoint_count = 0

        for chunk in exec_result.output:
            current_time = time.time()

            # Decode and collect the output
            line = chunk.decode('utf-8').strip()
            if line:
                print(f"  {line}")
                output_lines.append(line)

            # Check if it's time for a checkpoint
            elapsed_since_checkpoint = current_time - last_checkpoint_time
            if agent and elapsed_since_checkpoint >= checkpoint_interval:
                checkpoint_count += 1
                elapsed_total = current_time - start_time

                # Prepare checkpoint message
                current_output = "\n".join(output_lines)
                checkpoint_msg = f"\n{'='*60}\n"
                checkpoint_msg += f"CHECKPOINT #{checkpoint_count} (at {elapsed_total:.1f}s)\n"
                checkpoint_msg += f"{'='*60}\n"
                checkpoint_msg += f"Browser automation output so far:\n{current_output}\n"
                checkpoint_msg += f"{'='*60}\n"

                print(checkpoint_msg)

                # Add checkpoint to conversation history and ask agent
                observation_prompt = f"Observation: Browser automation task is still running (checkpoint #{checkpoint_count} at {elapsed_total:.1f}s). Output so far:\n{current_output}\n\nBased on the output so far, should I continue waiting or stop the task? Respond with just 'continue' or 'stop'."

                # Call agent with checkpoint
                response = agent(observation_prompt)

                print(f"\n  → Agent response: {response}\n")

                # Check if agent wants to stop
                if "stop" in response.lower() and "continue" not in response.lower():
                    print(f"\n  → Agent requested stop at {elapsed_total:.1f}s\n")
                    complete_output = "\n".join(output_lines)
                    return f"Browser automation stopped by agent decision at checkpoint #{checkpoint_count} ({elapsed_total:.1f}s):\n{complete_output}"

                # Update checkpoint time
                last_checkpoint_time = current_time

        # Task completed naturally
        complete_output = "\n".join(output_lines)
        elapsed_total = time.time() - start_time
        print(f"\n  → Browser automation completed after {elapsed_total:.1f}s\n")
        return f"Browser automation completed successfully (took {elapsed_total:.1f}s):\n{complete_output}"

    except docker.errors.DockerException as e:
        return f"Error connecting to Docker: {str(e)}"
    except Exception as e:
        return f"Error running browser automation: {str(e)}"


# Available tools
TOOLS: Dict[str, Callable] = {
    "calculate": calculate,
    "wait": wait,
    "count_test": count_test,
    "browser_automation": browser_automation,
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
                # Pass agent instance to tools that support checkpoint interactions
                if action_name in ["count_test", "browser_automation"]:
                    observation = TOOLS[action_name](action_input, agent=agent)
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
