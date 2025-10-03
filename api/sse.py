#!/usr/bin/env python3
"""
Gmail MCP Server - SSE Endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Set up SSE headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Cache-Control')
            self.end_headers()
            
            # Send initial connection event
            self.wfile.write(b'data: {"type": "connected", "message": "Gmail MCP Server connected"}\n\n')
            self.wfile.flush()
            
            # Import and run the MCP server
            try:
                from gmail_server import mcp
                
                # Send server info
                server_info = {
                    "type": "server_info",
                    "name": "Gmail MCP Server",
                    "version": "1.0.0",
                    "tools": [
                        "send_email",
                        "read_email", 
                        "search_emails",
                        "create_email_draft",
                        "get_unread_emails",
                        "manage_labels",
                        "batch_operations"
                    ]
                }
                self.wfile.write(f'data: {json.dumps(server_info)}\n\n'.encode())
                self.wfile.flush()
                
                # For Vercel, we'll run a simplified version
                # The full MCP server would need to be adapted for serverless
                self.wfile.write(b'data: {"type": "ready", "message": "Server ready for MCP connections"}\n\n')
                self.wfile.flush()
                
                # Keep connection alive
                import time
                while True:
                    time.sleep(30)
                    self.wfile.write(b'data: {"type": "ping", "timestamp": "' + str(int(time.time())).encode() + b'"}\n\n')
                    self.wfile.flush()
                    
            except ImportError as e:
                error_msg = {
                    "type": "error",
                    "message": f"Failed to import Gmail server: {str(e)}"
                }
                self.wfile.write(f'data: {json.dumps(error_msg)}\n\n'.encode())
                self.wfile.flush()
                
        except Exception as e:
            try:
                error_msg = {
                    "type": "error", 
                    "message": f"Server error: {str(e)}"
                }
                self.wfile.write(f'data: {json.dumps(error_msg)}\n\n'.encode())
                self.wfile.flush()
            except:
                pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Cache-Control')
        self.end_headers()
