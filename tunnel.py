#!/usr/bin/env python3
"""
Simple tunnel script using various services
"""
import subprocess
import time
import requests
import json

def try_localtunnel():
    """Try localtunnel"""
    try:
        print("Trying localtunnel...")
        process = subprocess.Popen(['npx', 'localtunnel', '--port', '8000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        
        # Wait a bit for it to start
        time.sleep(5)
        
        # Try to get the URL from the output
        try:
            stdout, stderr = process.communicate(timeout=2)
            print("Localtunnel output:", stdout)
            print("Localtunnel error:", stderr)
        except subprocess.TimeoutExpired:
            # Process is still running, which is good
            print("Localtunnel is running...")
            return True
    except Exception as e:
        print(f"Localtunnel failed: {e}")
        return False

def try_ngrok():
    """Try ngrok"""
    try:
        print("Trying ngrok...")
        process = subprocess.Popen(['./ngrok', 'http', '8000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Try to get the URL from ngrok's API
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            if response.status_code == 200:
                data = response.json()
                if 'tunnels' in data and len(data['tunnels']) > 0:
                    url = data['tunnels'][0]['public_url']
                    print(f"Ngrok URL: {url}")
                    return url
        except:
            pass
            
        return True
    except Exception as e:
        print(f"Ngrok failed: {e}")
        return False

def main():
    print("Setting up public tunnel for Gmail MCP Server...")
    print("Server is running on http://localhost:8000/sse")
    
    # Try ngrok first
    ngrok_result = try_ngrok()
    if ngrok_result and isinstance(ngrok_result, str):
        print(f"\n✅ Public URL: {ngrok_result}/sse")
        print("Press Ctrl+C to stop the tunnel")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping tunnel...")
            return
    
    # Try localtunnel
    if try_localtunnel():
        print("\n✅ Localtunnel started")
        print("Check the output above for the public URL")
        print("Press Ctrl+C to stop the tunnel")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping tunnel...")
            return
    
    print("❌ Could not establish tunnel")

if __name__ == "__main__":
    main()
