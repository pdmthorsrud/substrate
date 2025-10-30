#!/usr/bin/env python3
"""
Simple test script for Google Gemini Computer Use API.
This script tests the API connection by sending a simple prompt.
"""

import os
import sys
from datetime import datetime
from google import genai
from google.genai import types


def log(message: str) -> None:
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def main():
    """Main function to test Gemini Computer Use API."""

    log("🚀 Starting Gemini Computer Use API test")

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log("❌ ERROR: GOOGLE_API_KEY environment variable not set")
        log("Please set your API key: export GOOGLE_API_KEY='your-key-here'")
        return 1

    log(f"✅ API key found (length: {len(api_key)} characters)")

    # Initialize the Gemini client
    log("🔧 Initializing Gemini client...")
    try:
        client = genai.Client(api_key=api_key)
        log("✅ Client initialized successfully")
    except Exception as e:
        log(f"❌ Failed to initialize client: {e}")
        return 1

    # Define the model
    model_name = "gemini-2.5-computer-use-preview-10-2025"
    log(f"📋 Using model: {model_name}")

    # Create the prompt
    prompt = "can you please open nrk.no for me"
    log(f"💬 Sending prompt: '{prompt}'")

    # Configure the Computer Use tool
    log("🔧 Configuring Computer Use tool...")
    config = types.GenerateContentConfig(
        tools=[
            types.Tool(
                computer_use=types.ComputerUse(
                    environment=types.Environment.ENVIRONMENT_BROWSER
                )
            )
        ]
    )
    log("✅ Computer Use tool configured (environment: BROWSER)")

    # Create the request content
    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
    ]

    log("📤 Sending request to Gemini API...")
    log("=" * 60)

    try:
        # Generate content with Computer Use tool
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )

        log("=" * 60)
        log("✅ Response received successfully!")
        log("")
        log("📥 RESPONSE DETAILS:")
        log("-" * 60)

        # Print the full response
        if hasattr(response, 'text') and response.text:
            log(f"Response Text:\n{response.text}")
            log("")

        # Print candidates if available
        if hasattr(response, 'candidates') and response.candidates:
            log(f"Number of candidates: {len(response.candidates)}")
            for i, candidate in enumerate(response.candidates):
                log(f"\nCandidate {i + 1}:")

                if hasattr(candidate, 'content') and candidate.content:
                    content = candidate.content

                    # Check for parts (text and function calls)
                    if hasattr(content, 'parts') and content.parts:
                        log(f"  Number of parts: {len(content.parts)}")
                        for j, part in enumerate(content.parts):
                            log(f"\n  Part {j + 1}:")

                            # Check for text
                            if hasattr(part, 'text') and part.text:
                                log(f"    Type: Text")
                                log(f"    Content: {part.text}")

                            # Check for function call (Computer Use actions)
                            if hasattr(part, 'function_call') and part.function_call:
                                log(f"    Type: Function Call")
                                log(f"    Function: {part.function_call.name}")
                                log(f"    Arguments: {dict(part.function_call.args)}")

                if hasattr(candidate, 'finish_reason'):
                    log(f"\n  Finish reason: {candidate.finish_reason}")

        # Print usage metadata if available
        if hasattr(response, 'usage_metadata'):
            log(f"\nUsage Metadata:")
            log(f"  Prompt tokens: {response.usage_metadata.prompt_token_count}")
            log(f"  Candidates tokens: {response.usage_metadata.candidates_token_count}")
            log(f"  Total tokens: {response.usage_metadata.total_token_count}")

        log("-" * 60)
        log("")
        log("✨ Test completed successfully!")
        return 0

    except Exception as e:
        log("=" * 60)
        log(f"❌ Error during API call: {type(e).__name__}")
        log(f"Error message: {str(e)}")
        log("")

        # Print more details if available
        if hasattr(e, 'response'):
            log(f"Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
