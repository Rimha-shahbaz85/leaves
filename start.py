#!/usr/bin/env python3
"""
Startup script for Railway deployment
"""
import os
import sys
import subprocess

def main():
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Get port from Railway
    port = os.environ.get('PORT', '8501')
    
    # Start Streamlit with proper configuration
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'main.py',
        '--server.port', port,
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print(f"Starting Streamlit on port {port}...")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
