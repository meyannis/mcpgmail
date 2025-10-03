#!/usr/bin/env python3
"""
Gmail MCP Server - Health Check Endpoint
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check if Gmail MCP server is accessible
            server_status = "healthy"
            gmail_status = "unknown"
            
            # Try to import and check Gmail service
            try:
                from utils.auth import get_gmail_service
                service = get_gmail_service()
                # Try a simple API call
                profile = service.users().getProfile(userId='me').execute()
                gmail_status = "connected"
            except Exception as e:
                gmail_status = f"error: {str(e)[:100]}"
            
            health_data = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "Gmail MCP Server",
                "version": "1.0.0",
                "components": {
                    "server": {
                        "status": server_status,
                        "uptime": "running"
                    },
                    "gmail_api": {
                        "status": gmail_status,
                        "authenticated": gmail_status == "connected"
                    },
                    "mcp_endpoint": {
                        "status": "available",
                        "url": "/sse",
                        "transport": "Server-Sent Events"
                    }
                },
                "endpoints": {
                    "mcp": "/sse",
                    "health": "/health",
                    "web": "/"
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(health_data, indent=2).encode())
            
        except Exception as e:
            error_data = {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "service": "Gmail MCP Server"
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(error_data, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
