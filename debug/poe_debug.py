import sys
import os
import logging
from poe_api_wrapper import PoeApi

# Configurar caminho do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_logging():
    """Configurar logging detalhado"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('poe_debug.log'),  # Log em arquivo
            logging.StreamHandler(sys.stdout)      # Log no console
        ]
    )
    return logging.getLogger(__name__)

def debug_poe_api(tokens):
    """Função principal de debug"""
    logger = setup_logging()

    try:
        logger.info("Inicializando debug da Poe API")
        
        # Inicializar API
        api = PoeApi(tokens=tokens)
        
        # Testes de métodos
        logger.info("Testando métodos da API:")
        
        # Buscar bots disponíveis
        logger.info("Buscando bots disponíveis...")
        bots = api.get_available_bots()
        logger.info(f"Bots encontrados: {bots}")
        
        # Outros testes de método
        logger.info("Buscando categorias...")
        categories = api.get_available_categories()
        logger.info(f"Categorias encontradas: {categories}")
    
    except Exception as e:
        logger.error("Erro durante debug:", exc_info=True)
        logger.error("Possíveis causas:")
        logger.error("1. Tokens inválidos")
        logger.error("2. Problemas de conexão")
        logger.error("3. Mudanças na API")

def main():
    """Função principal para execução"""
    # IMPORTANTE: Substitua pelos seus tokens reais
    tokens = {
        'p-b': 'SEU_TOKEN_P_B',
        'p-lat': 'SEU_TOKEN_P_LAT'
    }
    
    debug_poe_api(tokens)

if __name__ == '__main__':
    main()