#!/usr/bin/env python3
"""
Gmail MCP Server - Web Interface
"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gmail MCP Server</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 2rem;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    text-align: center;
                    margin-bottom: 2rem;
                    font-size: 2.5rem;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }
                .status {
                    background: rgba(76, 175, 80, 0.2);
                    border: 1px solid rgba(76, 175, 80, 0.5);
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 1rem 0;
                    text-align: center;
                }
                .endpoint {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 1rem 0;
                    border-left: 4px solid #4CAF50;
                }
                .endpoint h3 {
                    margin-top: 0;
                    color: #4CAF50;
                }
                .code {
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 5px;
                    padding: 0.5rem;
                    font-family: 'Monaco', 'Menlo', monospace;
                    font-size: 0.9rem;
                    margin: 0.5rem 0;
                    word-break: break-all;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin: 2rem 0;
                }
                .feature {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 1rem;
                    text-align: center;
                }
                .feature-icon {
                    font-size: 2rem;
                    margin-bottom: 0.5rem;
                }
                a {
                    color: #4CAF50;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Gmail MCP Server</h1>
                
                <div class="status">
                    <h2>✅ Server Status: Online</h2>
                    <p>Your Gmail MCP Server is running and ready to handle requests!</p>
                </div>
                
                <div class="endpoint">
                    <h3>🔗 MCP Endpoint</h3>
                    <p>Connect your MCP clients to:</p>
                    <div class="code">/sse</div>
                    <p><strong>Full URL:</strong> <a href="/sse" target="_blank">https://your-domain.vercel.app/sse</a></p>
                </div>
                
                <div class="endpoint">
                    <h3>❤️ Health Check</h3>
                    <p>Monitor server health:</p>
                    <div class="code">/health</div>
                    <p><a href="/health" target="_blank">Check Health Status</a></p>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">📧</div>
                        <h3>Send Emails</h3>
                        <p>Plain text, HTML, with attachments</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔍</div>
                        <h3>Search & Read</h3>
                        <p>Powerful Gmail search and parsing</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">📝</div>
                        <h3>Manage Drafts</h3>
                        <p>Create, update, and send drafts</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🏷️</div>
                        <h3>Labels & Organization</h3>
                        <p>Manage labels and email organization</p>
                    </div>
                </div>
                
                <div class="endpoint">
                    <h3>🔧 Claude Desktop Configuration</h3>
                    <p>Add this to your Claude Desktop config:</p>
                    <div class="code">
{
  "mcpServers": {
    "gmail": {
      "command": "curl",
      "args": ["-N", "https://your-domain.vercel.app/sse"]
    }
  }
}
                    </div>
                </div>
                
                <div class="endpoint">
                    <h3>📚 Documentation</h3>
                    <p>Visit the <a href="https://github.com/meyannis/mcpgmail" target="_blank">GitHub repository</a> for full documentation and setup instructions.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
