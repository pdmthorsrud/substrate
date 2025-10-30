# ReAct Agent - Reasoning + Acting Pattern

A Python implementation of the ReAct (Reasoning + Acting) agent pattern using Google Gemini. This agent iteratively thinks about problems, decides on actions, executes tools, and processes observations to arrive at answers.

## What is ReAct?

ReAct is an AI agent pattern that combines **Reasoning** and **Acting** in an iterative loop:

```
Question → Thought → Action → PAUSE → Observation → Answer
```

1. **Thought**: The agent reasons about what to do
2. **Action**: The agent decides to use a tool
3. **PAUSE**: Execution stops while the tool runs
4. **Observation**: The tool result is fed back to the agent
5. **Answer**: The agent provides the final answer

This pattern allows the agent to break down complex problems into steps and use tools to gather information or perform calculations.

## Features

- 🤖 ReAct pattern implementation using Google Gemini
- 🧮 Built-in `calculate` tool for adding numbers
- 🔄 Automatic iteration with tool execution
- 📝 Verbose mode to see agent's reasoning
- 🎯 Pattern matching to detect actions and answers
- ⚡ Temperature set to 0 for deterministic responses

## Prerequisites

- Python 3.10 or higher
- Google API key (from Google AI Studio)

## Setup

### 1. Install Dependencies

```bash
cd react-agent
pip install -r requirements.txt
```

### 2. Set Your API Key

```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Get your API key from: https://aistudio.google.com/app/apikey

## Usage

### Run with Examples

```bash
python3 agent.py
```

This will run through several example queries showing the agent's reasoning process.

### Run with Custom Question

```bash
python3 agent.py "What is 25 + 75?"
```

### Programmatic Usage

```python
from agent import query
import os

api_key = os.getenv('GOOGLE_API_KEY')
answer = query("What is 100 + 200?", api_key, verbose=True)
print(f"Answer: {answer}")
```

## Example Output

```
============================================================
Question: What is 15 + 27?
============================================================

Turn 1:
Thought: I need to add 15 and 27 together.
Action: calculate: 15 + 27
PAUSE

  → Executing: calculate(15 + 27)
  ✓ Observation: 42

Turn 2:
Observation: 42
Answer: The result of 15 + 27 is 42.

============================================================
Final Answer: The result of 15 + 27 is 42.
============================================================
```

## How It Works

### 1. System Prompt

The agent is initialized with a system prompt that teaches it the ReAct pattern:

```python
SYSTEM_PROMPT = """You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.

Use Thought to describe what you're thinking about the question.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.
...
"""
```

### 2. Agent Class

The `Agent` class manages conversation history and executes Gemini API calls:

```python
class Agent:
    def __init__(self, system_message, api_key):
        # Initialize with system prompt

    def __call__(self, message):
        # Send message and get response

    def execute(self):
        # Call Gemini API
```

### 3. Tool Execution

Tools are Python functions that the agent can call:

```python
def calculate(expression: str) -> str:
    """Add two numbers together"""
    parts = expression.strip().split('+')
    num1 = float(parts[0].strip())
    num2 = float(parts[1].strip())
    return str(num1 + num2)

TOOLS = {
    "calculate": calculate,
}
```

### 4. Query Loop

The `query()` function runs the ReAct loop:

1. Send question to agent
2. Parse response for actions
3. Execute actions and get observations
4. Feed observations back to agent
5. Repeat until agent provides answer

```python
def query(question, api_key, max_turns=10):
    agent = Agent(SYSTEM_PROMPT, api_key)

    while counter < max_turns:
        result = agent(next_prompt)

        # Check for answer
        if "Answer:" in result:
            return extract_answer(result)

        # Check for action
        if action_found:
            observation = execute_tool(action)
            next_prompt = f"Observation: {observation}"
```

## Adding More Tools

To add new tools, define a function and register it:

```python
def multiply(expression: str) -> str:
    """Multiply two numbers"""
    parts = expression.strip().split('*')
    num1 = float(parts[0].strip())
    num2 = float(parts[1].strip())
    return str(num1 * num2)

TOOLS = {
    "calculate": calculate,
    "multiply": multiply,  # Add new tool
}
```

Then update the system prompt to include the new tool:

```python
SYSTEM_PROMPT = """
...
Your available actions are:

calculate:
e.g. calculate: 4 + 7
Adds two numbers together

multiply:
e.g. multiply: 4 * 7
Multiplies two numbers together
...
"""
```

## Configuration

### Change Model

Edit `agent.py` line 71:

```python
def __init__(self, system_message: str, api_key: str, model_name: str = "gemini-1.5-flash-latest"):
```

Available models:
- `gemini-1.5-flash-latest` (default) - Fast and cost-effective
- `gemini-1.5-pro-latest` - More capable, slower
- `gemini-2.0-flash-exp` - Experimental

### Adjust Max Turns

Limit the number of reasoning iterations:

```python
answer = query("What is 50 + 50?", api_key, max_turns=5)
```

### Disable Verbose Output

Hide intermediate reasoning steps:

```python
answer = query("What is 50 + 50?", api_key, verbose=False)
```

## Troubleshooting

### Error: "GOOGLE_API_KEY environment variable not set"

**Solution:** Set your API key:
```bash
export GOOGLE_API_KEY='your-actual-api-key'
python3 agent.py
```

### Error: "No module named 'google'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Agent Returns "Error: Unknown action"

**Solution:** Make sure the tool name in the action matches exactly:
- Correct: `Action: calculate: 10 + 20`
- Wrong: `Action: add: 10 + 20` (tool doesn't exist)

### Agent Reaches Max Turns

**Solution:**
1. Increase `max_turns` parameter
2. Improve system prompt clarity
3. Simplify the question
4. Check if tools are working correctly

### Calculate Function Error

**Solution:** Ensure expression is in format "number + number":
- Correct: `"15 + 27"`
- Wrong: `"15+27"` (no spaces)
- Wrong: `"15 plus 27"` (not numeric)

## Understanding the Pattern

### Why ReAct?

Traditional prompting gives the LLM a question and expects an immediate answer. ReAct allows the agent to:

1. **Break down problems** - Think step by step
2. **Use tools** - Access external capabilities
3. **Gather information** - Make multiple tool calls
4. **Reason iteratively** - Adjust based on observations

### When to Use ReAct

- Multi-step reasoning problems
- Questions requiring external tools/APIs
- Tasks needing calculations or lookups
- Complex queries that benefit from decomposition

### Pattern Comparison

**Direct Prompting:**
```
User: What is 15 + 27?
AI: 42
```

**ReAct:**
```
User: What is 15 + 27?
AI: [Thought] I need to add these numbers
    [Action] calculate: 15 + 27
    [PAUSE]
System: [Observation] 42
AI: [Answer] The result is 42
```

ReAct is more verbose but allows for tool usage and verified calculations.

## Extending the Agent

### Add API Tools

```python
import requests

def get_weather(location: str) -> str:
    """Get weather for a location"""
    # Call weather API
    response = requests.get(f"https://api.weather.com/v1/{location}")
    return response.json()['temperature']

TOOLS["get_weather"] = get_weather
```

### Add State Management

```python
class StatefulAgent(Agent):
    def __init__(self, system_message, api_key):
        super().__init__(system_message, api_key)
        self.state = {}  # Store agent state

    def update_state(self, key, value):
        self.state[key] = value
```

### Add Memory

```python
class MemoryAgent(Agent):
    def __init__(self, system_message, api_key):
        super().__init__(system_message, api_key)
        self.memory = []  # Store important facts

    def remember(self, fact):
        self.memory.append(fact)
```

## Resources

- [ReAct Paper](https://arxiv.org/abs/2210.03629) - Original research paper
- [LangGraph Course](https://learn.deeplearning.ai/courses/ai-agents-in-langgraph) - DeepLearning.AI course on agents
- [Google AI Studio](https://aistudio.google.com/) - Get API keys
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs) - Official documentation

## License

MIT License - Feel free to use and modify as needed.

## Next Steps

1. Try the example: `python3 agent.py`
2. Ask custom questions: `python3 agent.py "What is 99 + 1?"`
3. Add more tools (multiply, divide, etc.)
4. Experiment with different models
5. Build more complex agents!
