import os
import json

def save_poe_credentials(b, lat, formkey=None):
    """
    Salva as credenciais do Poe em um arquivo de configuração seguro.
    
    :param b: Token p-b
    :param lat: Token p-lat
    :param formkey: Formkey opcional
    """
    config_path = os.path.expanduser('~/.poe_config')
    credentials = {
        'p-b': b,
        'p-lat': lat,
        'formkey': formkey
    }
    
    # Remove chaves None
    credentials = {k: v for k, v in credentials.items() if v is not None}
    
    with open(config_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    # Definir permissões de arquivo para leitura/escrita apenas para o usuário
    try:
        os.chmod(config_path, 0o600)
    except Exception as e:
        print(f"Aviso: Não foi possível definir permissões restritas no arquivo: {e}")

def load_poe_credentials():
    """
    Carrega as credenciais do Poe do arquivo de configuração.
    
    :return: Dicionário de credenciais ou None se não encontrado
    """
    config_path = os.path.expanduser('~/.poe_config')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError) as e:
            print(f"Erro ao carregar credenciais: {e}")
    return None

def delete_poe_credentials():
    """
    Exclui o arquivo de credenciais do Poe.
    """
    config_path = os.path.expanduser('~/.poe_config')
    if os.path.exists(config_path):
        try:
            os.remove(config_path)
            print("Credenciais removidas com sucesso.")
        except Exception as e:
            print(f"Erro ao remover credenciais: {e}")

def get_tokens():
    """
    Obtém os tokens de credenciais do Poe.
    
    :return: Dicionário de tokens ou levanta exceção se não encontrados
    """
    credentials = load_poe_credentials()
    if not credentials:
        raise ValueError(
            "Nenhuma credencial encontrada. "
            "Use save_poe_credentials() para salvar suas credenciais primeiro."
        )
    
    # Verificar tokens necessários
    required_tokens = ['p-b', 'p-lat']
    for token in required_tokens:
        if token not in credentials:
            raise ValueError(f"Token '{token}' não encontrado nas credenciais.")
    
    return {
        'p-b': credentials['p-b'],
        'p-lat': credentials['p-lat']
    }

if __name__ == '__main__':
    import sys
    import os
    
    print("Caminho atual:", os.getcwd())
    print("Caminho do script:", os.path.abspath(__file__))
    print("Argumentos:", sys.argv)
    
    try:
        # Salvar credenciais de exemplo
        save_poe_credentials(
            b='UXe7h5W1V-EpZDUm6Qny7g%3D%3D', 
            lat='fFRUQ8A1MiT_7p7DEc_1XhZlTCTx1k0WLjsMF0knRsY-1739863678-1.0.1.1-4bqkjEtMFYWH8uFX0Ba.Xh71jrVlph2ItpcgaP3flE6mTZIa8JZbXRWvgoBk4YTWk4W0aJWTMfvn0RKWZi8QRw'
        )
        
        # Carregar e imprimir credenciais
        print('\nCredenciais salvas:')
        credentials = load_poe_credentials()
        print(credentials)
        
        # Testar recuperação de tokens
        print('\nRecuperando tokens:')
        tokens = get_tokens()
        print(tokens)
    
    except Exception as e:
        print(f"Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
