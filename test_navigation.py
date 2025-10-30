#!/usr/bin/env python3
"""
Simple browser automation test using Playwright.
This script navigates to nrk.no, takes a screenshot, and waits to demonstrate functionality.
"""

import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, Error as PlaywrightError

# Screen dimensions (recommended for Gemini Computer Use API)
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900


def log(message: str) -> None:
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def main():
    """Main function to run the browser automation test."""

    log("🚀 Starting Playwright browser automation test")

    # Configuration
    url = "https://nrk.no"
    screenshot_dir = "/app/screenshots"
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
    wait_time = 5  # seconds

    # Check if headless mode is requested via environment variable (default: true)
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    log(f"📋 Configuration:")
    log(f"   - Target URL: {url}")
    log(f"   - Headless mode: {headless}")
    log(f"   - Screen size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    log(f"   - Screenshot path: {screenshot_path}")
    log(f"   - Wait time: {wait_time} seconds")

    try:
        with sync_playwright() as p:
            log("🌐 Launching Chromium browser...")

            # Launch browser
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )

            log(f"✅ Browser launched successfully (headless={headless})")

            # Create a new browser context with recommended dimensions for Gemini Computer Use API
            context = browser.new_context(
                viewport={'width': SCREEN_WIDTH, 'height': SCREEN_HEIGHT},
            )

            log("📄 Creating new page...")
            page = context.new_page()

            log(f"🔗 Navigating to {url}...")

            # Navigate to the URL with timeout
            try:
                response = page.goto(url, timeout=5000)

                if response:
                    log(f"✅ Navigation successful! Status: {response.status}")
                else:
                    log("⚠️  Navigation completed but no response object returned")

            except PlaywrightError as e:
                log(f"❌ Navigation error: {e}")
                raise

            # Get page title
            title = page.title()
            log(f"📰 Page title: {title}")

            # Wait a moment for the page to fully render
            log("⏳ Waiting for page to fully render...")
            time.sleep(2)

            # Take a screenshot
            log(f"📸 Taking screenshot...")
            page.screenshot(path=screenshot_path, full_page=True)
            log(f"✅ Screenshot saved to: {screenshot_path}")

            # Check if file was created and get size
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                log(f"📊 Screenshot size: {file_size / 1024:.2f} KB")

            # Wait to demonstrate the browser is running
            log(f"⏸️  Waiting {wait_time} seconds to demonstrate functionality...")
            time.sleep(wait_time)

            # Get some page metrics
            url_after = page.url
            log(f"🔍 Final URL: {url_after}")

            # Close the browser
            log("🔚 Closing browser...")
            context.close()
            browser.close()

            log("✨ Test completed successfully!")
            return 0

    except PlaywrightError as e:
        log(f"❌ Playwright error occurred: {e}")
        return 1
    except Exception as e:
        log(f"❌ Unexpected error occurred: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
