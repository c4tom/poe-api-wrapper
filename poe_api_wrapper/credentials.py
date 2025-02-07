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
