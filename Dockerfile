# Use the official Playwright image with Chromium, Firefox, and WebKit pre-installed
FROM mcr.microsoft.com/playwright:v1.48.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install Python, VNC server, and noVNC dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    x11vnc \
    xvfb \
    fluxbox \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install noVNC and websockify
RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

# Create a symbolic link for python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for screenshots
RUN mkdir -p /app/screenshots

# Create VNC startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start Xvfb (X virtual framebuffer) on display :99\n\
echo "Starting Xvfb on display :99..."\n\
Xvfb :99 -screen 0 1280x720x24 -ac -nolisten tcp -nolisten unix &\n\
export DISPLAY=:99\n\
sleep 2\n\
\n\
# Start fluxbox window manager\n\
echo "Starting fluxbox..."\n\
fluxbox &\n\
sleep 1\n\
\n\
# Start x11vnc server (password-free, connected to display :99)\n\
echo "Starting x11vnc on port 5900..."\n\
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 &\n\
sleep 2\n\
\n\
# Start noVNC websocket proxy on port 6080\n\
echo "Starting noVNC on port 6080..."\n\
/opt/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &\n\
sleep 2\n\
\n\
echo ""\n\
echo "========================================"\n\
echo "VNC Setup Complete!"\n\
echo "========================================"\n\
echo "View in browser: http://localhost:6080"\n\
echo "VNC client: localhost:5900 (no password)"\n\
echo "Display: :99"\n\
echo "========================================"\n\
echo ""\n\
\n\
# Keep container running with interactive bash\n\
exec /bin/bash\n\
' > /usr/local/bin/start-vnc.sh && chmod +x /usr/local/bin/start-vnc.sh

# Set display environment variable
ENV DISPLAY=:99

# Default command - start VNC and bash shell
CMD ["/usr/local/bin/start-vnc.sh"]
