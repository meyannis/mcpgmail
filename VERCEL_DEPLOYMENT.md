# Vercel Deployment Guide

## Quick Deploy to Vercel

1. **Connect your GitHub repository to Vercel**
2. **Set up environment variables** in Vercel dashboard:
   - `GOOGLE_CLIENT_ID` - Your Google OAuth Client ID
   - `GOOGLE_CLIENT_SECRET` - Your Google OAuth Client Secret
   - `GMAIL_TOKEN_PATH` - Path to store tokens (optional)

3. **Deploy** - Vercel will automatically build and deploy

## Endpoints

- **`/`** - Web interface with server status and documentation
- **`/health`** - Health check endpoint (JSON)
- **`/sse`** - MCP Server-Sent Events endpoint

## Usage

### For Claude Desktop:
```json
{
  "mcpServers": {
    "gmail": {
      "command": "curl",
      "args": ["-N", "https://your-app.vercel.app/sse"]
    }
  }
}
```

### For Testing:
- Visit `https://your-app.vercel.app/` for the web interface
- Visit `https://your-app.vercel.app/health` for health status
- Connect to `https://your-app.vercel.app/sse` for MCP

## Environment Variables

Make sure to set these in your Vercel project settings:

- `GOOGLE_CLIENT_ID` - Required for Gmail API authentication
- `GOOGLE_CLIENT_SECRET` - Required for Gmail API authentication

## Notes

- The serverless environment has limitations for long-running connections
- For production use, consider using a dedicated server or VPS
- The SSE endpoint is adapted for serverless but may have connection timeouts
