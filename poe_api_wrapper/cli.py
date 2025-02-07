import argparse
from importlib import metadata
from poe_api_wrapper import PoeExample
from .credentials import save_poe_credentials, load_poe_credentials

def main():
    parser = argparse.ArgumentParser(prog='poe',description='Poe.com wrapper. Have free access to ChatGPT, Claude, Llama, Gemini, Google-PaLM and more!')
    parser.add_argument('-b', help='p-b token for poe.com', required=False)
    parser.add_argument('-lat', help='p-lat token for poe.com', required=False)
    parser.add_argument('-f', help='formkey for poe.com', required=False)
    parser.add_argument('--save', action='store_true', help='Save the provided credentials for future use')
    parser.add_argument('--clear', action='store_true', help='Clear saved credentials')
    parser.add_argument('-v', '--version', action='version', version='v'+metadata.version('poe-api-wrapper'))
    
    args = parser.parse_args()

    # Limpar credenciais
    if args.clear:
        from .credentials import delete_poe_credentials
        delete_poe_credentials()
        return

    # Carregar credenciais salvas se não forem fornecidas
    if not (args.b and args.lat):
        saved_credentials = load_poe_credentials()
        if saved_credentials:
            args.b = args.b or saved_credentials.get('p-b')
            args.lat = args.lat or saved_credentials.get('p-lat')
            args.f = args.f or saved_credentials.get('formkey')

    # Verificar se todas as credenciais necessárias estão presentes
    if not (args.b and args.lat):
        parser.error("Tokens p-b e p-lat são obrigatórios. Use -b e -lat ou configure com --save.")

    # Salvar credenciais se solicitado
    if args.save:
        save_poe_credentials(args.b, args.lat, args.f)
        print("Credenciais salvas com sucesso!")

    # Preparar tokens para uso
    tokens = {'p-b': args.b, 'p-lat': args.lat}
    if args.f:
        tokens['formkey'] = args.f

    PoeExample(tokens).chat_with_bot()

if __name__=='__main__':
    main()