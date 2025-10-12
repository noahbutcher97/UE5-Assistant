"""Quick bootstrap - run this single line in UE5 Python console."""

# Copy and paste this entire command into UE5 Python console:
exec("""
import os, sys, zipfile, tarfile, tempfile, shutil, requests, unreal
SERVER = "https://ue5-assistant-noahbutcher97.replit.app"
print("🚀 BOOTSTRAPPING UE5 AI ASSISTANT...")
r = requests.get(f"{SERVER}/api/download_client", timeout=30)
c = r.content
with tempfile.TemporaryDirectory() as tmp:
    if c[:2] == b'PK':  # ZIP
        p = f"{tmp}/c.zip"
        with open(p, 'wb') as f: f.write(c)
        with zipfile.ZipFile(p, 'r') as z: z.extractall(tmp)
    else:  # TAR.GZ
        p = f"{tmp}/c.tar.gz"
        with open(p, 'wb') as f: f.write(c)
        with tarfile.open(p, 'r:gz') as t: t.extractall(tmp)
    target = os.path.join(unreal.Paths.project_content_dir(), "Python", "AIAssistant")
    if os.path.exists(target): shutil.rmtree(target + "_old", ignore_errors=True); shutil.move(target, target + "_old")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copytree(f"{tmp}/AIAssistant", target)
[sys.modules.pop(k) for k in list(sys.modules.keys()) if 'AIAssistant' in k]
sys.path.append(os.path.dirname(target)) if os.path.dirname(target) not in sys.path else None
import AIAssistant.startup; AIAssistant.startup.configure_and_start()
print("✅ AI ASSISTANT READY!")
""")