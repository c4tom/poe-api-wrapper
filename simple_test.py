print("Teste simples de importação")
import sys
import os

print("Python Path:", sys.path)
print("Current Working Directory:", os.getcwd())
print("Script Path:", os.path.abspath(__file__))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from poe_api_wrapper import credentials
    print("Módulo importado com sucesso!")
except Exception as e:
    print(f"Erro na importação: {e}")
    import traceback
    traceback.print_exc()
