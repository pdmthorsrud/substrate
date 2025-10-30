# VNC Access Guide

Watch the Playwright browser in real-time as Gemini AI controls it!

## Quick Start

### 1. Rebuild and Start the Container

```bash
# Stop and remove existing container
docker-compose down

# Rebuild with VNC support
docker-compose build

# Start the container
docker-compose up -d
```

### 2. Access VNC in Your Browser

**Recommended Method:** Open your web browser and navigate to:

```
http://localhost:6080
```

Click "Connect" and you'll immediately see the desktop with the browser!

**No password required** - it's configured for password-free local development.

### 3. Verify VNC is Working

Before running any Gemini scripts, verify VNC is set up correctly:

```bash
# Check that VNC services are running
docker logs playwright-browser
```

You should see output like:
```
Starting Xvfb on display :99...
Starting fluxbox...
Starting x11vnc on port 5900...
Starting noVNC on port 6080...
========================================
VNC Setup Complete!
========================================
View in browser: http://localhost:6080
VNC client: localhost:5900 (no password)
Display: :99
========================================
```

### 4. Test with a Simple Browser Command

Open a shell in the container and test that the browser appears in VNC:

```bash
# Get a shell in the container
docker exec -it playwright-browser /bin/bash

# Run a simple Playwright test to verify browser appears in VNC
python3 test_navigation.py
```

You should see the browser window appear in your VNC viewer at http://localhost:6080!

### 5. Run Gemini Computer Use

Now run your Gemini script and watch the AI control the browser:

```bash
docker exec -it playwright-browser python3 gemini_computer_use.py "open nrk.no"
```

Watch in your browser at http://localhost:6080 as Gemini opens the browser and navigates to the site!

## Connection Methods

### Method 1: Web Browser (Recommended)

- **URL:** http://localhost:6080
- **Password:** None (password-free)
- **Advantages:** No client software needed, works in any browser
- **Best for:** Quick access and demonstrations

Simply open http://localhost:6080 in Chrome, Firefox, Safari, or any modern browser.

### Method 2: VNC Client (Alternative)

If you prefer using a native VNC client:

- **Host:** localhost
- **Port:** 5900
- **Password:** None

VNC client recommendations:
- **macOS:** Built-in Screen Sharing or RealVNC Viewer
- **Windows:** TightVNC Viewer or RealVNC Viewer
- **Linux:** Remmina or Vinagre

## Technical Details

### VNC Configuration

- **Display:** :99
- **Resolution:** 1280x720x24
- **VNC Port:** 5900 (for VNC clients)
- **noVNC Port:** 6080 (for web browser access)
- **Authentication:** Disabled (password-free)
- **Window Manager:** fluxbox

### Architecture

```
┌─────────────────────────────────────────┐
│          Docker Container               │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Xvfb (Virtual X Server)         │  │
│  │  Display :99                     │  │
│  │  Resolution: 1280x720            │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Playwright Browser              │  │
│  │  (Controlled by Gemini AI)       │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  x11vnc Server                   │  │
│  │  Port: 5900                      │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  noVNC + websockify              │  │
│  │  Port: 6080                      │  │
│  └──────────────────────────────────┘  │
│               │                         │
└───────────────┼─────────────────────────┘
                │
                ▼
        Your Web Browser
     http://localhost:6080
```

## Troubleshooting

### Can't Access http://localhost:6080

**Solution 1:** Check if the container is running
```bash
docker-compose ps
```

**Solution 2:** Check if ports are properly exposed
```bash
docker ps
# Look for: 0.0.0.0:6080->6080/tcp and 0.0.0.0:5900->5900/tcp
```

**Solution 3:** Check container logs
```bash
docker logs playwright-browser
```

### VNC Shows Blank Screen

**Solution 1:** The browser might be headless. Check environment:
```bash
docker exec playwright-browser printenv HEADLESS
# Should be "false"
```

**Solution 2:** Restart the container
```bash
docker-compose restart
```

### Browser Not Appearing in VNC

**Solution 1:** Verify DISPLAY is set correctly
```bash
docker exec playwright-browser printenv DISPLAY
# Should be ":99"
```

**Solution 2:** Check that Xvfb is running
```bash
docker exec playwright-browser ps aux | grep Xvfb
```

### Port Already in Use

If ports 5900 or 6080 are already in use on your host:

**Solution:** Change the ports in docker-compose.yml
```yaml
ports:
  - "5901:5900"  # Change 5901 to any free port
  - "6081:6080"  # Change 6081 to any free port
```

Then access via http://localhost:6081

## Tips and Best Practices

### 1. Keep VNC Open While Running Scripts

Open http://localhost:6080 **before** running your Gemini scripts to watch the automation happen in real-time.

### 2. Maximize the Browser Window

The VNC shows a 1280x720 desktop. If you want a different resolution, modify the Dockerfile:

```dockerfile
Xvfb :99 -screen 0 1920x1080x24 ...  # Change to desired resolution
```

Then rebuild: `docker-compose build`

### 3. Multiple Monitors

You can connect multiple VNC clients simultaneously (web browser + VNC client) to watch from different locations.

### 4. Recording Sessions

To record what happens in VNC:
- **Browser Method:** Use browser screen recording extensions
- **VNC Client Method:** Many VNC clients have built-in recording features

## Switching Between Headless and Headed Mode

### To Use VNC (Headed Mode - See Browser)

In docker-compose.yml:
```yaml
environment:
  - HEADLESS=false
```

### To Use Headless Mode (No VNC - Faster)

In docker-compose.yml:
```yaml
environment:
  - HEADLESS=true
```

Then restart: `docker-compose restart`

## Next Steps

1. Open http://localhost:6080 in your browser
2. Run: `docker exec -it playwright-browser python3 gemini_computer_use.py "open nrk.no"`
3. Watch the magic happen!

## Security Note

**WARNING:** This VNC setup has no password and is intended for local development only.

**DO NOT:**
- Expose port 5900 or 6080 to the internet
- Use this configuration in production
- Share your localhost ports publicly

This is safe for local development because the ports are only accessible from your machine (localhost).
