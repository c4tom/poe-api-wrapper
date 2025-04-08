import sys
import os
import traceback

print("Python Path:", sys.path)
print("Current Working Directory:", os.getcwd())
print("Script Path:", os.path.abspath(__file__))

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from poe_api_wrapper.credentials import save_poe_credentials, load_poe_credentials, get_tokens

    # Salvar credenciais
    save_poe_credentials(
        b='UXe7h5W1V-EpZDUm6Qny7g%3D%3D', 
        lat='fFRUQ8A1MiT_7p7DEc_1XhZlTCTx1k0WLjsMF0knRsY-1739863678-1.0.1.1-4bqkjEtMFYWH8uFX0Ba.Xh71jrVlph2ItpcgaP3flE6mTZIa8JZbXRWvgoBk4YTWk4W0aJWTMfvn0RKWZi8QRw'
    )

    # Carregar e imprimir credenciais
    print('Credenciais salvas:')
    print(load_poe_credentials())

    # Testar recuperação de tokens
    print('\nRecuperando tokens:')
    tokens = get_tokens()
    print(tokens)

except Exception as e:
    print(f"Erro: {e}")
    traceback.print_exc()
