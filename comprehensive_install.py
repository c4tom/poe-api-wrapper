import subprocess
import sys
import os

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Command successful: {command}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error output: {e.stderr}")
        return False
    return True

def setup_virtual_environment():
    print("Setting up virtual environment...")
    if not os.path.exists('venv'):
        run_command(f"{sys.executable} -m venv venv")
    
    # Determine the correct pip based on the virtual environment
    pip_path = os.path.join('venv', 'Scripts', 'pip') if sys.platform == 'win32' else os.path.join('venv', 'bin', 'pip')
    
    # Activate virtual environment and upgrade pip
    run_command(f"{pip_path} install --upgrade pip setuptools wheel")
    
    # Install project and its dependencies
    run_command(f"{pip_path} install -e .[llm,proxy,web_search]")
    
    # Install specific problematic packages
    run_command(f"{pip_path} install fastapi-poe ballyregan")

def main():
    print("=== COMPREHENSIVE POE API WRAPPER INSTALLER ===")
    setup_virtual_environment()
    print("\n🎉 Installation process completed!")

if __name__ == '__main__':
    main()
