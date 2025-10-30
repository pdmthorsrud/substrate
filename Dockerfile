# Use the official Playwright image with Chromium, Firefox, and WebKit pre-installed
FROM mcr.microsoft.com/playwright:v1.48.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install Python and pip (python3 and pip3 are already in the base image)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

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

# Default command - run the Python script directly
CMD ["python3", "test_navigation.py"]
