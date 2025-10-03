#!/usr/bin/env python3
"""
Simple tunnel using a different approach
"""
import subprocess
import time
import sys

def main():
    print("🚀 Creating public tunnel for Gmail MCP Server...")
    print("📍 Local server: http://localhost:8000/sse")
    
    # Try using localtunnel with explicit output
    try:
        print("\n🔗 Starting localtunnel...")
        process = subprocess.Popen(
            ['npx', 'localtunnel', '--port', '8000', '--subdomain', 'gmail-mcp'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("⏳ Waiting for tunnel to establish...")
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            print(f"📝 {line.strip()}")
            if 'https://' in line and 'localtunnel' in line:
                url = line.strip().split()[-1] if line.strip().split() else ""
                if url.startswith('https://'):
                    print(f"\n✅ SUCCESS! Your Gmail MCP Server is now public!")
                    print(f"🌐 Public URL: {url}/sse")
                    print(f"🔗 Full endpoint: {url}/sse")
                    print("\n📋 Usage:")
                    print(f"   - For MCP clients: {url}/sse")
                    print(f"   - For testing: Visit {url}/sse in browser")
                    print("\n⏹️  Press Ctrl+C to stop the tunnel")
                    
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 Stopping tunnel...")
                        process.terminate()
                        return
                        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Alternative: You can manually run:")
        print("   npx localtunnel --port 8000")

if __name__ == "__main__":
    main()
