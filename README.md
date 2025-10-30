# Playwright Docker Browser Automation

A Docker-based browser automation system using Playwright and Python. This is a foundation setup that can be extended with AI-controlled browser actions (e.g., Google's Gemini Computer Use API).

## Features

- 🐳 Docker containerized environment with official Playwright image
- 🎭 Playwright with Chromium browser pre-installed
- 🐍 Python 3 with all necessary dependencies
- 📸 Screenshot capture functionality
- 🖥️ Headless mode by default (optimized for Docker)
- 🔄 Easy setup with docker-compose
- ✅ Works on both Linux and macOS
- ⚡ Proper Docker configuration following Playwright best practices

## Prerequisites

- Docker Desktop (macOS) or Docker Engine (Linux)
- Docker Compose (usually included with Docker Desktop)

## Project Structure

```
.
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── test_navigation.py     # Browser automation test script
├── .dockerignore         # Files to exclude from Docker build
├── screenshots/           # Directory for saved screenshots
└── README.md             # This file
```

## Quick Start

### 1. Build the Docker Image

Using docker-compose (recommended):
```bash
docker-compose build
```

Or using Docker directly:
```bash
docker build -t playwright-automation:latest .
```

### 2. Run the Container

Using docker-compose (recommended):
```bash
docker-compose up
```

Or using Docker directly:
```bash
docker run --rm \
  --init \
  --ipc=host \
  -v $(pwd)/screenshots:/app/screenshots \
  --shm-size=2gb \
  playwright-automation:latest
```

### 3. Verify the Test Worked

After the container runs, you should see:
- Detailed logs showing each step of the browser automation
- A screenshot saved in the `./screenshots/` directory
- A success message at the end

Check the screenshot:
```bash
ls -lh screenshots/
```

## Configuration Options

### Headless Mode

By default, the browser runs in **headless mode** (no visible browser window), which is the recommended setting for Docker environments.

To disable headless mode (not recommended in Docker without additional setup), set the `HEADLESS` environment variable:

```bash
# Using docker-compose (edit docker-compose.yml)
environment:
  - HEADLESS=false

# Or using Docker directly
docker run --rm \
  --init \
  --ipc=host \
  -e HEADLESS=false \
  -v $(pwd)/screenshots:/app/screenshots \
  --shm-size=2gb \
  playwright-automation:latest
```

**Note:** Headed mode (HEADLESS=false) requires additional setup with Xvfb or similar X11 virtual display server, which is not included in this basic setup.

### Modifying the Test Script

The test script is mounted as a volume, so you can edit `test_navigation.py` and run the container again without rebuilding:

```bash
# Edit the script
vim test_navigation.py

# Run again
docker-compose up
```

## Understanding the Output

The script provides detailed logging:

```
[2024-01-15 10:30:00] 🚀 Starting Playwright browser automation test
[2024-01-15 10:30:00] 📋 Configuration:
[2024-01-15 10:30:00]    - Target URL: https://nrk.no
[2024-01-15 10:30:00]    - Headless mode: true
[2024-01-15 10:30:00]    - Screenshot path: /app/screenshots/screenshot_1705318200.png
[2024-01-15 10:30:00]    - Wait time: 5 seconds
[2024-01-15 10:30:01] 🌐 Launching Chromium browser...
[2024-01-15 10:30:02] ✅ Browser launched successfully (headless=true)
[2024-01-15 10:30:02] 📄 Creating new page...
[2024-01-15 10:30:02] 🔗 Navigating to https://nrk.no...
[2024-01-15 10:30:03] ✅ Navigation successful! Status: 200
[2024-01-15 10:30:03] 📰 Page title: NRK – Nyheter, TV og Radio
[2024-01-15 10:30:03] ⏳ Waiting for page to fully render...
[2024-01-15 10:30:05] 📸 Taking screenshot...
[2024-01-15 10:30:06] ✅ Screenshot saved to: /app/screenshots/screenshot_1705318200.png
[2024-01-15 10:30:06] 📊 Screenshot size: 456.78 KB
[2024-01-15 10:30:06] ⏸️  Waiting 5 seconds to demonstrate functionality...
[2024-01-15 10:30:11] 🔍 Final URL: https://www.nrk.no/
[2024-01-15 10:30:11] 🔚 Closing browser...
[2024-01-15 10:30:11] ✨ Test completed successfully!
```

## Troubleshooting

### Issue: "Browser closed" or "Connection refused" errors

**Solution:** Increase shared memory size. Chrome requires sufficient shared memory:
```bash
docker run --shm-size=2gb ...
```

### Issue: Screenshots are not appearing in the screenshots directory

**Solution:** Make sure the directory exists and is properly mounted:
```bash
mkdir -p screenshots
docker-compose up
```

### Issue: Permission denied errors on Linux

**Solution:** Adjust permissions on the screenshots directory:
```bash
chmod 777 screenshots
```

### Issue: Container exits immediately

**Solution:** Check logs for errors:
```bash
docker-compose logs
```

## Development Tips

### Running Interactively

To debug or develop inside the container:
```bash
docker run -it --rm \
  --init \
  --ipc=host \
  -v $(pwd)/screenshots:/app/screenshots \
  -v $(pwd)/test_navigation.py:/app/test_navigation.py \
  --shm-size=2gb \
  --entrypoint /bin/bash \
  playwright-automation:latest
```

Then inside the container:
```bash
python3 test_navigation.py
```

### Docker Configuration Explained

This setup follows [Playwright's Docker best practices](https://playwright.dev/docs/docker):

- **`--init`**: Prevents zombie processes by avoiding special treatment for PID=1
- **`--ipc=host`**: Allows Chromium to use shared memory, preventing out-of-memory crashes
- **`--shm-size=2gb`**: Allocates sufficient shared memory for browser operations
- **`cap_add: SYS_ADMIN`** (optional, commented out): May help with unusual Chromium launch errors during local development

### Customizing the Browser

Edit `test_navigation.py` to modify:
- Target URL
- Browser settings
- Viewport size
- Wait times
- Screenshot options

Example customization:
```python
# Change URL
url = "https://example.com"

# Change viewport
context = browser.new_context(
    viewport={'width': 1280, 'height': 720}
)

# Take partial screenshot
page.screenshot(path=screenshot_path, full_page=False)
```

## Next Steps: AI Integration

This setup provides a foundation for integrating AI-controlled browser automation. Future enhancements could include:

1. **Google Gemini Computer Use API**: Integrate LLM-based decision making
2. **Action Recording**: Log all browser actions for training/debugging
3. **Dynamic Navigation**: AI determines navigation paths
4. **Content Extraction**: Intelligent data scraping
5. **Form Automation**: AI-driven form filling

## Cleanup

Remove containers and images:
```bash
# Stop and remove containers
docker-compose down

# Remove the image
docker rmi playwright-automation:latest

# Remove all screenshots
rm -rf screenshots/*
```

## Resources

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Playwright Docker Guide](https://playwright.dev/docs/docker)
- [Playwright Docker Images](https://mcr.microsoft.com/en-us/product/playwright/python/about)
- [Google Gemini Computer Use API](https://ai.google.dev/gemini-api/docs/computer-use)
- [Docker Documentation](https://docs.docker.com/)

## License

This project is provided as-is for educational and development purposes.
