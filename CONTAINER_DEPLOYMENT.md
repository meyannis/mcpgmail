# Containerized Deployment Guide

This guide covers deploying the Gmail MCP Server using Docker containers on various platforms.

## 🐳 Docker Support

The server now supports containerized deployment with proper SSE support for long-lived connections.

### Local Development

```bash
# Build the image
docker build -t gmail-mcp-server .

# Run locally
docker run -p 8080:8080 \
  -e GOOGLE_CLIENT_ID=your_client_id \
  -e GOOGLE_CLIENT_SECRET=your_client_secret \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  gmail-mcp-server
```

### Using Docker Compose

```bash
# Set environment variables
export GOOGLE_CLIENT_ID=your_client_id
export GOOGLE_CLIENT_SECRET=your_client_secret

# Start the service
docker-compose up -d
```

## 🚀 Platform Deployments

### Render

1. **Connect your GitHub repository**
2. **Create a new Web Service**
3. **Configure:**
   - Environment: Docker
   - Dockerfile Path: `./Dockerfile`
   - Port: 8080
4. **Set environment variables:**
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
5. **Deploy!**

The `render.yaml` file is included for automatic configuration.

### Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and create app:**
   ```bash
   fly auth login
   fly launch
   ```

3. **Set secrets:**
   ```bash
   fly secrets set GOOGLE_CLIENT_ID=your_client_id
   fly secrets set GOOGLE_CLIENT_SECRET=your_client_secret
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

The `fly.toml` file is included for configuration.

### Railway

1. **Connect your GitHub repository**
2. **Create a new project**
3. **Set environment variables:**
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
4. **Deploy!**

The `railway.json` file is included for configuration.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | Yes |
| `GMAIL_TOKEN_PATH` | Path to store OAuth tokens | No (default: `/app/token.json`) |

### Port Configuration

- **Default Port:** 8080
- **Health Check:** `/health`
- **MCP Endpoint:** `/sse`
- **Web Interface:** `/`

## 📋 Endpoints

### `/` - Root
Returns service information and available endpoints.

### `/health` - Health Check
Returns server status and Gmail API connection status.

### `/sse` - MCP Endpoint
Server-Sent Events endpoint for MCP client connections.

## 🔗 Usage

### For Claude Desktop:
```json
{
  "mcpServers": {
    "gmail": {
      "command": "curl",
      "args": ["-N", "https://your-app-url.com/sse"]
    }
  }
}
```

### For Testing:
- Visit `https://your-app-url.com/` for service info
- Visit `https://your-app-url.com/health` for health status
- Connect to `https://your-app-url.com/sse` for MCP

## 🛠️ Development

### Local Testing

```bash
# Run with Docker
docker run -p 8080:8080 gmail-mcp-server

# Or run directly
python gmail_server.py --sse 0.0.0.0:8080
```

### Building

```bash
# Build image
docker build -t gmail-mcp-server .

# Test locally
docker run -p 8080:8080 gmail-mcp-server
```

## 📝 Notes

- The containerized version uses FastAPI + Uvicorn for better SSE support
- Long-lived connections are properly supported (unlike serverless)
- Health checks are included for all platforms
- Automatic restart policies are configured
- CORS headers are set for web access
