#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Computer Use - Interactive Browser Automation with Loop

This script sends prompts to Gemini Computer Use API and executes
the returned function calls using Playwright in a continuous loop
until the task is complete.

Usage:
    python3 gemini_computer_use.py "open nrk.no"
    python3 gemini_computer_use.py "go to wikipedia.org and search for Python"
"""

import os
import sys
import base64
from datetime import datetime
from pathlib import Path
from io import BytesIO

from playwright.sync_api import sync_playwright, Page, Browser
from google import genai
from google.genai import types
from PIL import Image


def log(message: str):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def initialize_browser(playwright):
    """Initialize and return a Playwright browser and page"""
    log("Initializing browser...")

    # Launch browser (headless mode based on environment variable)
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    browser = playwright.chromium.launch(headless=headless)

    # Create browser context and page
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720}
    )
    page = context.new_page()

    log("Browser initialized successfully")
    return browser, page


def take_screenshot(page: Page, step_number: int) -> tuple[bytes, str]:
    """
    Take a screenshot, compress it, and return the bytes and mime type
    Also saves original to disk for debugging

    Returns:
        tuple: (compressed_screenshot_bytes, mime_type)
    """
    # Take screenshot as bytes
    screenshot_bytes = page.screenshot()

    # Save original to disk for debugging
    screenshots_dir = Path("/app/screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_step_{step_number}.png"
    filepath = screenshots_dir / filename

    with open(filepath, 'wb') as f:
        f.write(screenshot_bytes)

    log(f"Screenshot saved: {filename}")

    # Compress screenshot to reduce token usage
    # Open the screenshot with PIL
    img = Image.open(BytesIO(screenshot_bytes))

    # Resize to smaller dimensions (512x288 from 1280x720 = 40% of original)
    # This reduces tokens by ~85%
    new_size = (512, 288)
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

    # Convert to JPEG with quality 75 to further reduce size
    output = BytesIO()
    img_resized.save(output, format='JPEG', quality=75, optimize=True)
    compressed_bytes = output.getvalue()

    original_kb = len(screenshot_bytes) / 1024
    compressed_kb = len(compressed_bytes) / 1024
    log(f"Screenshot compressed: {original_kb:.1f}KB -> {compressed_kb:.1f}KB ({compressed_kb/original_kb*100:.1f}%)")

    return compressed_bytes, "image/jpeg"


def execute_open_web_browser(page: Page, args: dict):
    """Execute open_web_browser function call"""
    log("Executing: open_web_browser")
    # Since browser is already initialized, navigate to blank page
    page.goto("about:blank")
    log("Browser opened (navigated to about:blank)")


def execute_navigate(page: Page, args: dict):
    """Execute navigate function call"""
    url = args.get('url')

    if not url:
        log("ERROR: No URL provided in navigate arguments")
        return

    log(f"Executing: navigate to {url}")

    # Navigate to the URL
    page.goto(url, wait_until='domcontentloaded', timeout=30000)

    log(f"Successfully navigated to {url}")


def execute_function_call(function_name: str, function_args: dict, page: Page):
    """Execute the appropriate function based on function_name"""

    if function_name == "open_web_browser":
        execute_open_web_browser(page, function_args)

    elif function_name == "navigate":
        execute_navigate(page, function_args)

    else:
        log(f"WARNING: Unknown function '{function_name}' (not yet implemented)")


def parse_function_call(response):
    """
    Parse function call from Gemini response
    Returns: (function_call_part, function_name, function_args) or (None, None, None)
    """
    if not response.candidates:
        return None, None, None

    candidate = response.candidates[0]

    if not candidate.content or not candidate.content.parts:
        return None, None, None

    for part in candidate.content.parts:
        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            function_name = function_call.name
            function_args = dict(function_call.args) if function_call.args else {}

            return part, function_name, function_args

    return None, None, None


def main():
    """Main execution function with Computer Use loop"""

    # Get prompt from command line argument
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_computer_use.py \"your prompt here\"")
        print("\nExamples:")
        print("  python3 gemini_computer_use.py \"open nrk.no\"")
        print("  python3 gemini_computer_use.py \"go to wikipedia.org\"")
        sys.exit(1)

    initial_prompt = sys.argv[1]

    log("Starting Gemini Computer Use")
    log("=" * 60)

    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        log("ERROR: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    log(f"API key found (length: {len(api_key)} characters)")

    # Initialize Gemini client
    log("Initializing Gemini client...")
    client = genai.Client(api_key=api_key)
    log("Gemini client initialized")

    # Model configuration
    model_name = "gemini-2.5-computer-use-preview-10-2025"
    config = types.GenerateContentConfig(
        tools=[
            types.Tool(
                computer_use=types.ComputerUse(
                    environment=types.Environment.ENVIRONMENT_BROWSER
                )
            )
        ],
        temperature=0.0,
    )

    # Initialize Playwright and browser
    with sync_playwright() as playwright:
        browser, page = initialize_browser(playwright)

        try:
            # Initialize conversation history with initial prompt
            conversation_history = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=initial_prompt)]
                )
            ]

            log("=" * 60)
            log(f"Initial prompt: '{initial_prompt}'")

            # Computer Use loop
            step = 0
            max_steps = 50  # Safety limit to prevent infinite loops

            while step < max_steps:
                step += 1
                log("=" * 60)
                log(f"STEP {step}: Sending request to Gemini...")

                # Send request to Gemini with conversation history
                response = client.models.generate_content(
                    model=model_name,
                    contents=conversation_history,
                    config=config
                )

                log("Response received from Gemini")

                # Parse function call from response
                function_call_part, function_name, function_args = parse_function_call(response)

                if function_name:
                    log(f"Function call: {function_name}")
                    if function_args:
                        log(f"Arguments: {function_args}")

                    # Execute the function call
                    execute_function_call(function_name, function_args, page)

                    # Take screenshot of new state
                    log("Taking screenshot of current state...")
                    screenshot_bytes, mime_type = take_screenshot(page, step)

                    # Encode screenshot as base64 for sending to Gemini
                    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

                    # Get current page URL
                    current_url = page.url
                    log(f"Current URL: {current_url}")

                    # Add assistant's response to conversation history
                    conversation_history.append(
                        types.Content(
                            role="model",
                            parts=[function_call_part]
                        )
                    )

                    # Create function response with screenshot and URL
                    function_response = types.FunctionResponse(
                        name=function_name,
                        response={
                            "url": current_url,
                            "screenshot": {
                                "mime_type": mime_type,
                                "data": screenshot_base64
                            }
                        }
                    )

                    # Add function response to conversation history
                    conversation_history.append(
                        types.Content(
                            role="user",
                            parts=[types.Part(function_response=function_response)]
                        )
                    )

                    log(f"Screenshot and URL sent back to Gemini as function response")

                    # Continue loop to get next action
                    continue

                else:
                    # No function call - task is complete
                    log("=" * 60)
                    log("No function call returned - task completed!")

                    # Check if there's a text response
                    if response.candidates and response.candidates[0].content:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'text') and part.text:
                                log(f"Gemini says: {part.text}")

                    break

            if step >= max_steps:
                log("=" * 60)
                log(f"WARNING: Reached maximum steps ({max_steps})")

            log("=" * 60)
            log(f"Total steps executed: {step}")
            log("Task execution completed!")

        except Exception as e:
            log(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            # Keep browser open briefly to see final state
            log("Keeping browser open for 2 seconds...")
            page.wait_for_timeout(2000)

            # Close browser
            browser.close()
            log("Browser closed")


if __name__ == "__main__":
    main()
