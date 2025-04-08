import os
import sys
import subprocess
import shutil

def print_header(message):
    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)

def check_current_environment():
    print_header("CURRENT ENVIRONMENT DETAILS")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Version: {sys.version}")
    print("\nPython Path:")
    for path in sys.path:
        print(path)

def reinstall_project():
    print_header("REINSTALLING PROJECT DEPENDENCIES")
    commands = [
        f"{sys.executable} -m pip install --upgrade pip setuptools wheel",
        f"{sys.executable} -m pip uninstall -y poe-api-wrapper",
        f"{sys.executable} -m pip install -e .[llm,proxy,web_search]",
        f"{sys.executable} -m pip install fastapi-poe ballyregan"
    ]
    
    for cmd in commands:
        print(f"\nRunning: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
        else:
            print(f"✅ Command successful")

def create_local_venv():
    print_header("CREATING LOCAL VIRTUAL ENVIRONMENT")
    project_root = r'd:\temp\poe-api-wrapper-ct'
    venv_path = os.path.join(project_root, 'venv')
    
    # Remove existing venv if it exists
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
    
    # Create new virtual environment
    subprocess.run(f"{sys.executable} -m venv {venv_path}", shell=True, check=True)
    
    print(f"Virtual environment created at: {venv_path}")

def verify_imports():
    print_header("VERIFYING MODULE IMPORTS")
    modules_to_check = [
        'fastapi_poe', 
        'ballyregan', 
        'poe_api_wrapper', 
        'poe_api_wrapper.api', 
        'poe_api_wrapper.cli'
    ]
    
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✅ Successfully imported: {module}")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")

def main():
    check_current_environment()
    create_local_venv()
    reinstall_project()
    verify_imports()
    print("\n🎉 Environment setup complete!")

if __name__ == '__main__':
    main()
