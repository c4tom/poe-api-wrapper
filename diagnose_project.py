import sys
import platform
import importlib

def check_python_version():
    print("Python Version Check:")
    print(f"Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Python executable: {sys.executable}")
    print("\n")

def check_dependencies():
    dependencies = [
        'httpx', 'websocket_client', 'requests_toolbelt', 'loguru', 'rich', 
        'beautifulsoup4', 'quickjs', 'nest_asyncio', 'orjson', 'aiofiles', 
        'markdown2', 'plantuml', 'flask', 'six', 'fastapi_poe', 'ballyregan'
    ]
    
    print("Dependency Check:")
    for dep in dependencies:
        try:
            importlib.import_module(dep.replace('-', '_'))
            print(f"✅ {dep}: Installed")
        except ImportError:
            print(f"❌ {dep}: NOT INSTALLED")
    print("\n")

def check_project_modules():
    project_modules = [
        'poe_api_wrapper.cli', 
        'poe_api_wrapper.sqlitize', 
        'poe_api_wrapper.search_chats', 
        'poe_api_wrapper.chat_web_search'
    ]
    
    print("Project Modules Check:")
    for module in project_modules:
        try:
            __import__(module)
            print(f"✅ {module}: Importable")
        except ImportError as e:
            print(f"❌ {module}: IMPORT ERROR - {e}")
    print("\n")

def main():
    print("=== POE API WRAPPER DIAGNOSTIC TOOL ===")
    check_python_version()
    check_dependencies()
    check_project_modules()

if __name__ == '__main__':
    main()
