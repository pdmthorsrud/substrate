# Testing Guide

This guide explains how to test code inside the Docker container using an interactive workflow.

## Testing Workflow

The recommended approach for testing is to:
1. Run the container in detached mode
2. Get an interactive terminal inside the container using `docker exec`
3. Run **anything** you need inside the container - tests, Python files, shell commands, experiments, etc.

This workflow allows you to iterate quickly without rebuilding the container or starting it repeatedly.

## Step-by-Step Instructions

### 1. Build the Docker Image

First, ensure the image is built:

```bash
docker-compose build
```

### 2. Start the Container in Detached Mode

Start the container in the background:

```bash
docker-compose up -d
```

This will start the `playwright-browser` container and keep it running in detached mode.

### 3. Get an Interactive Terminal Inside the Container

Execute an interactive bash shell inside the running container:

```bash
docker exec -it playwright-browser /bin/bash
```

You'll now have a shell prompt inside the container (e.g., `root@abc123:/app#`).

### 4. Run Anything You Need

Once inside the container, you can run **any commands or scripts** you need:

```bash
# Test the Gemini API connection
python3 test_gemini_api.py

# Test browser navigation
python3 test_navigation.py

# Run any Python code directly
python3 -c "print('Hello from inside the container!')"

# Test specific Python functions interactively
python3
>>> from test_gemini_api import some_function
>>> some_function()

# Run shell commands
ls -la
pwd
env | grep GOOGLE

# Test Playwright installation
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright is working!')"

# Check Python version and installed packages
python3 --version
pip list

# Install and test new packages on the fly
pip install requests
python3 -c "import requests; print(requests.get('https://httpbin.org/get').json())"

# Create and run experimental scripts
cat > experiment.py << 'EOF'
print("Testing something new")
EOF
python3 experiment.py

# Check network connectivity
curl https://google.com
ping -c 3 8.8.8.8

# Debug environment variables
printenv

# Run bash scripts
bash your_script.sh
```

**The key point:** You have full shell access inside the container. You can run absolutely anything - Python scripts, shell commands, install packages, create new files, experiment with code, debug issues, etc.

### 5. Exit the Container Shell

When done testing, exit the interactive shell:

```bash
exit
```

The container will continue running in the background.

### 6. Stop the Container

When you're completely done testing:

```bash
docker-compose down
```

## Quick Reference Commands

### Container Management

```bash
# Start container in detached mode
docker-compose up -d

# Check if container is running
docker-compose ps

# View container logs
docker-compose logs -f

# Stop the container
docker-compose down

# Restart the container
docker-compose restart
```

### Interactive Testing

```bash
# Get a shell inside the running container
docker exec -it playwright-browser /bin/bash

# Run a single command inside the container without interactive shell
docker exec playwright-browser python3 test_gemini_api.py

# Run any shell command
docker exec playwright-browser ls -la /app

# Run Python code directly
docker exec playwright-browser python3 -c "print('test')"

# Copy files into the container (if needed)
docker cp local-file.py playwright-browser:/app/

# Copy files from the container to host
docker cp playwright-browser:/app/output.txt ./
```

## Common Testing Scenarios

### Scenario 1: Quick One-Off Test

If you just want to run a single script without an interactive shell:

```bash
docker-compose up -d
docker exec playwright-browser python3 test_gemini_api.py
docker-compose down
```

### Scenario 2: Iterative Development

For iterative testing (recommended):

```bash
# Start once
docker-compose up -d

# Get interactive shell
docker exec -it playwright-browser /bin/bash

# Inside the container, run multiple tests and commands
python3 test_gemini_api.py
python3 test_navigation.py
ls -la screenshots/
# ... make changes to files on host (mounted volumes) ...
python3 test_gemini_api.py  # Run again with changes
# ... experiment with anything you need ...

# Exit when done
exit

# Stop container
docker-compose down
```

### Scenario 3: Debugging and Experimentation

For debugging with full flexibility:

```bash
docker-compose up -d
docker exec -it playwright-browser /bin/bash

# Inside container - do whatever you need:
# - Test individual functions
# - Install new packages
# - Create temporary scripts
# - Debug environment issues
# - Run interactive Python sessions
# - Test API calls manually
# - Whatever you need!

python3
>>> import os
>>> print(os.getenv('GOOGLE_API_KEY'))
>>> # Test anything interactively
```

### Scenario 4: Live Debugging with Logs

For debugging with live logs:

```bash
# Terminal 1: Start and watch logs
docker-compose up

# Terminal 2: In a separate terminal, exec into container
docker exec -it playwright-browser /bin/bash

# Inside container, run tests or any commands
python3 test_gemini_api.py

# You'll see logs in Terminal 1
```

## Mounted Volumes

The docker-compose.yml mounts these directories/files:

- `./screenshots:/app/screenshots` - Screenshots taken by Playwright
- `./test_navigation.py:/app/test_navigation.py` - Navigation test script
- `./test_gemini_api.py:/app/test_gemini_api.py` - API test script

**Important:** Changes to mounted files on your host will be immediately reflected inside the container. You don't need to rebuild or restart the container.

To add more files to the container:
1. **Option A:** Add them to docker-compose.yml volumes and restart the container
2. **Option B:** Use `docker cp` to copy files into the running container
3. **Option C:** Create them directly inside the container shell (temporary, lost on restart)

## Environment Variables

The container loads environment variables from `.env` file. To verify they're set:

```bash
docker exec -it playwright-browser /bin/bash
env | grep GOOGLE_API_KEY
```

## Troubleshooting

### Container Not Running

```bash
# Check status
docker-compose ps

# If not running, start it
docker-compose up -d

# Check logs for errors
docker-compose logs
```

### Can't Execute Into Container

```bash
# Check container name
docker ps

# Use full docker command if docker-compose doesn't work
docker exec -it playwright-browser /bin/bash
```

### Permission Issues

```bash
# If you get permission errors with screenshots or files
docker exec -it playwright-browser /bin/bash
chmod -R 777 /app/screenshots
```

### Python Package Not Found

```bash
# Inside the container, install missing packages
pip install package-name

# Or rebuild the image with the package in requirements.txt
```

### Environment Variables Not Set

```bash
# Verify .env file exists on host
cat .env

# Restart container to reload environment
docker-compose restart

# Verify inside container
docker exec playwright-browser env | grep GOOGLE_API_KEY
```

## Testing Checklist

Before running tests, ensure:

- [ ] Docker container is running (`docker-compose ps`)
- [ ] `.env` file exists and contains `GOOGLE_API_KEY`
- [ ] Required Python files are mounted or copied into container
- [ ] Container has network access (for API calls)

## Advanced: Running Tests with Screenshots

```bash
# Start container
docker-compose up -d

# Run test that takes screenshots
docker exec playwright-browser python3 test_navigation.py

# Screenshots will appear in ./screenshots/ on your host
ls -la screenshots/
```

## Alternative: One-Line Test Commands

Instead of docker-compose, you can use direct docker commands:

```bash
# Run container in detached mode
docker run -d \
  --name playwright-test \
  --init \
  --ipc=host \
  --env-file .env \
  -v "$(pwd)/screenshots:/app/screenshots" \
  -v "$(pwd)/test_gemini_api.py:/app/test_gemini_api.py" \
  playwright-automation:latest \
  tail -f /dev/null

# Exec into it and run anything
docker exec -it playwright-test /bin/bash

# Clean up when done
docker stop playwright-test
docker rm playwright-test
```

## Summary

**Recommended workflow for testing:**

1. `docker-compose up -d` - Start container in background
2. `docker exec -it playwright-browser /bin/bash` - Get interactive shell
3. Inside container: **Run anything you need** - Python scripts, shell commands, experiments, debugging, etc.
4. `exit` - Leave container (it keeps running)
5. `docker-compose down` - Stop when completely done

This approach gives you the fastest iteration cycle for testing and development. You have full control to run any commands, scripts, or experiments you need inside the containerized environment.
