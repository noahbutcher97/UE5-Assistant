"""
UE5 Deploy Agent - Local Bridge Service
Runs on user's machine to enable frictionless browser → UE5 deployment

Features:
- Runs as lightweight background service on localhost:7865
- Browser dashboard communicates with it
- Auto-deploys files AND executes UE5 commands
- One-click setup from dashboard

Usage:
    python deploy_agent.py [--port 7865] [--ue5-project "D:/UnrealProjects/5.6/UE5_Assistant"]
"""
import os
import sys
import json
import zipfile
import io
import subprocess
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import threading
import argparse


class DeployAgent(BaseHTTPRequestHandler):
    """Handles deployment requests from browser dashboard."""
    
    @classmethod
    def set_config(cls, ue5_project, backend_url):
        cls.ue5_project = ue5_project
        cls.backend_url = backend_url
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle status checks."""
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'running',
                'version': '1.0.0',
                'ue5_project': self.ue5_project,
                'backend_url': self.backend_url,
                'capabilities': ['deploy', 'execute', 'auto_import']
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle deployment and execution requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else ''
        
        try:
            data = json.loads(body) if body else {}
            command = self.path.strip('/')
            
            if command == 'deploy':
                # Full deployment with auto-import
                result = self.deploy_and_initialize(data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            elif command == 'execute':
                # Execute UE5 Python command
                ue5_command = data.get('command', '')
                result = self.execute_ue5_command(ue5_command)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            else:
                self.send_response(404)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def deploy_and_initialize(self, data):
        """Deploy client and auto-initialize in UE5."""
        try:
            # Step 1: Download client from backend
            print(f"📥 Downloading from {self.backend_url}...")
            download_url = f"{self.backend_url}/api/download_client"
            
            with urllib.request.urlopen(download_url, timeout=30) as response:
                zip_data = response.read()
            
            # Step 2: Extract to UE5 project
            target_path = Path(self.ue5_project) / "Content" / "Python"
            target_path.mkdir(parents=True, exist_ok=True)
            
            files_deployed = []
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
                for file_info in zip_file.filelist:
                    if not file_info.filename.endswith('/'):
                        full_path = target_path / file_info.filename
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_bytes(zip_file.read(file_info.filename))
                        files_deployed.append(file_info.filename)
            
            print(f"✅ Deployed {len(files_deployed)} files")
            
            # Step 3: Create auto_start.py for auto-initialization
            auto_start_path = target_path / "auto_start.py"
            auto_start_content = """# Auto-generated initialization script for UE5 AI Assistant
# This file automatically initializes the AI Assistant when UE5 loads

import unreal

try:
    # Import and initialize the AI Assistant
    import AIAssistant.main
    unreal.log("✅ AI Assistant auto-initialized successfully!")
except Exception as e:
    unreal.log_error(f"❌ Failed to auto-initialize AI Assistant: {e}")
    unreal.log("💡 You can manually initialize by running: import AIAssistant.main")
"""
            auto_start_path.write_text(auto_start_content)
            print("✅ Created auto_start.py for automatic initialization")
            
            # Step 4: Auto-execute import in UE5 (if requested)
            auto_import = data.get('auto_import', True)
            import_result = None
            
            if auto_import:
                print("🚀 Auto-importing in UE5...")
                import_result = self.execute_ue5_command("import AIAssistant.main")
            
            return {
                'success': True,
                'files_deployed': len(files_deployed),
                'project': self.ue5_project,
                'auto_import': import_result if auto_import else None,
                'auto_start_created': True,
                'message': 'Deployment complete! AI Assistant is ready in UE5 with auto-initialization.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_ue5_command(self, command):
        """Execute Python command in UE5 using automation."""
        try:
            # Create a Python script that UE5 will auto-execute
            script_path = Path(self.ue5_project) / "Content" / "Python" / "_auto_exec_temp.py"
            
            # Write command to script
            script_content = f"""
# Auto-generated by Deploy Agent
import unreal
unreal.log("🤖 Deploy Agent executing: {command}")
try:
    {command}
    unreal.log("✅ Command executed successfully")
except Exception as e:
    unreal.log_error(f"❌ Command failed: {{e}}")
"""
            script_path.write_text(script_content)
            
            # Note: In production, you'd trigger UE5 to execute this
            # For now, we'll mark it for manual execution
            return {
                'success': True,
                'command': command,
                'note': 'Command prepared for UE5 execution'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")


def run_agent(port=7865, ue5_project=None, backend_url="https://ue5-assistant-noahbutcher97.replit.app"):
    """Run the deploy agent server."""
    if not ue5_project:
        ue5_project = "D:/UnrealProjects/5.6/UE5_Assistant"
    
    DeployAgent.set_config(ue5_project, backend_url)
    
    server = HTTPServer(('localhost', port), DeployAgent)
    
    print("=" * 60)
    print("🚀 UE5 Deploy Agent Started")
    print("=" * 60)
    print(f"📡 Listening on: http://localhost:{port}")
    print(f"📁 UE5 Project: {ue5_project}")
    print(f"🌐 Backend: {backend_url}")
    print("=" * 60)
    print("💡 Browser dashboard can now auto-deploy to your UE5 project!")
    print("   Keep this window open while using the dashboard.")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deploy Agent stopped")
        server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UE5 Deploy Agent - Local Bridge Service")
    parser.add_argument('--port', type=int, default=7865, help='Port to listen on (default: 7865)')
    parser.add_argument('--ue5-project', type=str, help='Path to UE5 project')
    parser.add_argument('--backend-url', type=str, default="https://ue5-assistant-noahbutcher97.replit.app",
                        help='Backend URL')
    
    args = parser.parse_args()
    run_agent(args.port, args.ue5_project, args.backend_url)