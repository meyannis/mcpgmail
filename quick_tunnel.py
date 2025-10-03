#!/usr/bin/env python3
"""
Quick tunnel using a simple approach
"""
import subprocess
import time
import sys

def main():
    print("🚀 Creating public tunnel for Gmail MCP Server...")
    print("📍 Local server: http://localhost:8000/sse")
    
    # Try using localtunnel with a simple approach
    try:
        print("\n🔗 Starting localtunnel...")
        print("⏳ This may take a moment...")
        
        # Run localtunnel and capture output
        result = subprocess.run(
            ['npx', 'localtunnel', '--port', '8000'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Look for the URL in the output
        output = result.stdout + result.stderr
        print(f"📝 Output: {output}")
        
        # Extract URL from output
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'loca.lt' in line:
                url = line.strip()
                if url.startswith('https://'):
                    print(f"\n✅ SUCCESS! Your Gmail MCP Server is now public!")
                    print(f"🌐 Public URL: {url}/sse")
                    print(f"🔗 Full endpoint: {url}/sse")
                    print("\n📋 Usage:")
                    print(f"   - For MCP clients: {url}/sse")
                    print(f"   - For testing: Visit {url}/sse in browser")
                    return url
                    
        print("❌ Could not extract URL from localtunnel output")
        print("💡 Try running manually: npx localtunnel --port 8000")
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout waiting for localtunnel")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Alternative: You can manually run:")
        print("   npx localtunnel --port 8000")

if __name__ == "__main__":
    main()
