# Setup Guide

This guide will help you set up the Google Gemini Computer Use API for browser automation.

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud account (for API key)
- Python 3.10+ (if running locally without Docker)

## Getting Your Google Gemini API Key

### Step 1: Access Google AI Studio

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account

### Step 2: Create an API Key

1. Click on **"Get API key"** or **"Create API key"**
2. Select an existing Google Cloud project or create a new one
3. Click **"Create API key in existing project"** or **"Create API key in new project"**
4. Copy the generated API key immediately (you won't be able to see it again)

### Step 3: Store Your API Key Securely

**IMPORTANT:** Never commit your API key to version control!

#### Option 1: Environment Variable (Recommended for local testing)

```bash
# On macOS/Linux
export GOOGLE_API_KEY='your_api_key_here'

# On Windows (PowerShell)
$env:GOOGLE_API_KEY='your_api_key_here'

# On Windows (Command Prompt)
set GOOGLE_API_KEY=your_api_key_here
```

#### Option 2: .env File (Recommended for development)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```bash
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

3. The `.env` file is already in `.gitignore` and will NOT be committed to Git

## Installation

### Docker Setup (Recommended)

1. **Build the Docker image:**
   ```bash
   docker-compose build
   ```

2. **Create your `.env` file** (see above)

3. **Run the Gemini API test:**
   ```bash
   docker run --rm \
     --init \
     --ipc=host \
     --env-file .env \
     playwright-automation:latest \
     python3 test_gemini_api.py
   ```

### Local Setup (Alternative)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

3. **Create your `.env` file** (see above)

4. **Load environment variables:**
   ```bash
   # On macOS/Linux
   source .env

   # Or use python-dotenv in your scripts
   ```

5. **Run the Gemini API test:**
   ```bash
   python3 test_gemini_api.py
   ```

## Testing the API Connection

Run the test script to verify your API key works:

```bash
# With Docker
docker run --rm --init --ipc=host --env-file .env \
  playwright-automation:latest python3 test_gemini_api.py

# Locally
python3 test_gemini_api.py
```

You should see output like:

```
[2024-01-15 10:30:00] 🚀 Starting Gemini Computer Use API test
[2024-01-15 10:30:00] ✅ API key found (length: 39 characters)
[2024-01-15 10:30:00] 🔧 Initializing Gemini client...
[2024-01-15 10:30:00] ✅ Client initialized successfully
[2024-01-15 10:30:00] 📋 Using model: gemini-2.5-computer-use-preview-10-2025
[2024-01-15 10:30:00] 💬 Sending prompt: 'can you please open nrk.no for me'
[2024-01-15 10:30:00] 📤 Sending request to Gemini API...
[2024-01-15 10:30:01] ✅ Response received successfully!
[2024-01-15 10:30:01] ✨ Test completed successfully!
```

## Troubleshooting

### Error: "GOOGLE_API_KEY environment variable not set"

**Solution:** Make sure you've set the environment variable or created a `.env` file with your API key.

### Error: "Invalid API key"

**Solution:**
- Verify your API key is correct
- Check that you've enabled the Gemini API in your Google Cloud project
- Ensure your API key hasn't been restricted or revoked

### Error: "Permission denied" or "API not enabled"

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Library**
4. Search for "Generative Language API" or "Gemini API"
5. Click **Enable**

### Error: "Model not found" or "Model not accessible"

**Solution:** The Gemini Computer Use API model (`gemini-2.5-computer-use-preview-10-2025`) is in preview. Ensure you have access to preview features.

## API Usage Limits

- Free tier: Check [Google AI Studio pricing](https://ai.google.dev/pricing) for current limits
- Rate limits apply - implement appropriate retry logic for production use
- Monitor your usage in Google Cloud Console

## Security Best Practices

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Rotate API keys regularly** - Create new keys periodically
3. **Use separate keys** for development and production
4. **Restrict API keys** - In Google Cloud Console, restrict keys by:
   - IP address
   - HTTP referrer
   - Application (Android/iOS)
5. **Monitor usage** - Watch for unexpected API calls

## Next Steps

Once your API key is working:

1. **See [TESTING.md](TESTING.md)** for detailed instructions on interactive testing inside the container
2. Test the browser automation: `docker-compose up`
3. Integrate Gemini with Playwright for full Computer Use functionality
4. Review the [Gemini Computer Use API documentation](https://ai.google.dev/gemini-api/docs/computer-use)

## Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Gemini Computer Use API Guide](https://ai.google.dev/gemini-api/docs/computer-use)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Pricing](https://ai.google.dev/pricing)
