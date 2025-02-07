import os
import json
import sqlite3
import argparse
import re
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

class ChatSearcher:
    def __init__(self, database_path: str):
        """
        Inicializa o buscador de chats
        
        :param database_path: Caminho para o banco de dados SQLite
        """
        self.console = Console()
        self.database_path = os.path.abspath(database_path)
        
        if not os.path.exists(self.database_path):
            self.console.print(f"[red]Erro: Banco de dados {self.database_path} não encontrado.[/red]")
            raise FileNotFoundError(f"Banco de dados {self.database_path} não existe.")
    
    def _connect(self):
        """Conecta ao banco de dados SQLite"""
        return sqlite3.connect(self.database_path)
    
    def search_messages(self, 
                        query: str, 
                        bot_name: str = None, 
                        regex: bool = False, 
                        case_sensitive: bool = False, 
                        whole_word: bool = False):
        """
        Busca mensagens no banco de dados
        
        :param query: Texto ou padrão de busca
        :param bot_name: Nome do bot para filtrar (opcional)
        :param regex: Usar expressão regular
        :param case_sensitive: Busca sensível a maiúsculas/minúsculas
        :param whole_word: Buscar palavra completa
        :return: Lista de resultados
        """
        conn = self._connect()
        cursor = conn.cursor()
        
        # Preparar condições de busca
        conditions = []
        params = []
        
        # Filtro por bot, se especificado
        if bot_name:
            conditions.append("bot_name = ?")
            params.append(bot_name)
        
        # Preparar query de busca
        if regex:
            # Usar REGEXP do SQLite
            conditions.append("messages REGEXP ?")
            params.append(query)
        else:
            # Preparar busca por texto
            search_pattern = query
            
            if whole_word:
                search_pattern = r'\b' + re.escape(search_pattern) + r'\b'
            
            if not case_sensitive:
                conditions.append("LOWER(messages) LIKE LOWER(?)")
                params.append(f"%{search_pattern}%")
            else:
                conditions.append("messages LIKE ?")
                params.append(f"%{search_pattern}%")
        
        # Construir consulta SQL
        sql_query = """
        SELECT id, bot_name, chat_title, chat_id, messages 
        FROM chat_history
        """
        
        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def display_results(self, results, query):
        """
        Exibe resultados da busca de forma formatada
        
        :param results: Resultados da busca
        :param query: Termo de busca
        """
        if not results:
            self.console.print("[yellow]Nenhum resultado encontrado.[/yellow]")
            return
        
        table = Table(title="Resultados da Busca")
        table.add_column("Bot", style="cyan")
        table.add_column("Chat", style="magenta")
        table.add_column("Ocorrências", style="green")
        
        for result in results:
            _, bot_name, chat_title, chat_id, messages_json = result
            
            try:
                messages = json.loads(messages_json)
                
                # Contar ocorrências
                matching_messages = [
                    msg for msg in messages 
                    if query.lower() in str(msg).lower() or 
                       query.lower() in str(msg.get('text', '')).lower() or
                       query.lower() in str(msg.get('content', '')).lower()
                ]
                
                table.add_row(
                    str(bot_name), 
                    str(chat_title), 
                    str(len(matching_messages))
                )
            except Exception as e:
                self.console.print(f"[red]Erro ao processar mensagens: {e}[/red]")
        
        self.console.print(table)

def interactive_mode(searcher):
    """
    Modo interativo de busca com prompt de comando
    
    :param searcher: Instância do ChatSearcher
    """
    console = Console()
    console.print("[bold green]Modo interativo de busca de chats[/bold green]")
    console.print("Digite \\h para ajuda, \\q para sair")
    
    help_text = r"""
    Comandos disponíveis:
    \h, help     - Mostrar esta ajuda
    \q, quit     - Sair do modo interativo
    
    Sintaxe de busca:
    <termo> [-b BOT] [-r] [-c] [-w]
    
    Opções:
    -b, --bot    Filtrar por nome do bot
    -r, --regex  Usar expressão regular
    -c, --case   Busca sensível a maiúsculas
    -w, --whole  Buscar palavra completa
    
    Exemplos:
    python                   Busca simples
    python -b gemini         Busca em bot específico
    "^import" -r             Busca com regex
    """
    
    while True:
        try:
            query = console.input("[bold cyan]search> [/bold cyan]")
            
            # Comandos especiais
            if query in ['\\q', 'quit']:
                break
            elif query in ['\\h', 'help']:
                console.print(Syntax(help_text, "markdown"))
                continue
            
            # Parsing de argumentos
            args = query.split()
            
            # Separar termo de busca e opções
            search_term = args[0]
            options = {
                'bot': None,
                'regex': False,
                'case_sensitive': False,
                'whole_word': False
            }
            
            # Processar opções
            for arg in args[1:]:
                if arg in ['-b', '--bot']:
                    options['bot'] = args[args.index(arg) + 1]
                elif arg in ['-r', '--regex']:
                    options['regex'] = True
                elif arg in ['-c', '--case']:
                    options['case_sensitive'] = True
                elif arg in ['-w', '--whole']:
                    options['whole_word'] = True
            
            # Realizar busca
            results = searcher.search_messages(
                query=search_term,
                bot_name=options['bot'],
                regex=options['regex'],
                case_sensitive=options['case_sensitive'],
                whole_word=options['whole_word']
            )
            
            searcher.display_results(results, search_term)
        
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(description='Busca avançada em histórico de chats')
    parser.add_argument('database', help='Caminho do banco de dados SQLite')
    parser.add_argument('-i', '--interactive', action='store_true', help='Modo interativo')
    
    # Manter opções antigas para compatibilidade
    parser.add_argument('query', nargs='?', default=None, help='Texto ou padrão de busca')
    parser.add_argument('-b', '--bot', help='Filtrar por nome do bot')
    parser.add_argument('-r', '--regex', action='store_true', help='Usar expressão regular')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='Busca sensível a maiúsculas/minúsculas')
    parser.add_argument('-w', '--whole-word', action='store_true', help='Buscar palavra completa')
    
    args = parser.parse_args()
    
    try:
        searcher = ChatSearcher(args.database)
        
        # Modo interativo tem prioridade
        if args.interactive or not args.query:
            interactive_mode(searcher)
        else:
            # Modo de busca única
            results = searcher.search_messages(
                query=args.query,
                bot_name=args.bot,
                regex=args.regex,
                case_sensitive=args.case_sensitive,
                whole_word=args.whole_word
            )
            
            searcher.display_results(results, args.query)
    
    except Exception as e:
        Console().print(f"[red]Erro: {e}[/red]")

if __name__ == '__main__':
    main()
