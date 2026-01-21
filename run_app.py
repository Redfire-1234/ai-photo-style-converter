import subprocess
import threading
import time
import webbrowser
import os
from pathlib import Path

def run_backend():
    """Run FastAPI backend"""
    os.chdir(Path(__file__).parent / 'backend')
    subprocess.run(['python', 'app.py'])

def run_frontend():
    """Run frontend server"""
    import http.server
    import socketserver
    
    os.chdir(Path(__file__).parent / 'frontend')
    
    PORT = 3000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎨 AI PHOTO STYLE CONVERTER")
    print("="*70)
    
    # Start backend in thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait for backend to start
    print("⏳ Starting backend server...")
    time.sleep(3)
    
    # Start frontend in thread
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    # Wait for frontend to start
    time.sleep(2)
    
    print("✅ Backend API: http://localhost:8000")
    print("✅ Frontend UI: http://localhost:3000")
    print("\n" + "="*70)
    print("🌐 CLICK HERE TO OPEN APP:")
    print("👉 http://localhost:3000")
    print("="*70)
    print("\n💡 Press Ctrl+C to stop both servers\n")
    
    # Auto-open browser
    time.sleep(1)
    try:
        webbrowser.open('http://localhost:3000')
    except:
        pass
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down servers...")
        print("✓ Stopped successfully\n")