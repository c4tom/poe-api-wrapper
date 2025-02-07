# Importações padrão do Python
import os
import json
import sqlite3
import html
import re
import base64
from datetime import datetime  # Importação correta do datetime
import argparse
from typing import List, Dict, Any

# Importações de terceiros
import markdown2
import requests
import plantuml
from rich.console import Console  # Adicionar importação do Console

# Importações do Flask e relacionadas
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Importações para syntax highlighting
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

class ChatWebSearcher:
    def __init__(self, database_path: str):
        """
        Inicializa o buscador web de chats
        
        :param database_path: Caminho para o banco de dados SQLite
        """
        # Importar módulos necessários
        import re
        self.re = re
        
        self.console = Console()
        self.database_path = os.path.abspath(database_path)
        
        if not os.path.exists(self.database_path):
            self.console.print(f"[red]Erro: Banco de dados {self.database_path} não encontrado.[/red]")
            raise FileNotFoundError(f"Banco de dados {self.database_path} não existe.")
        
        # Configurar PlantUML
        self.plantuml_server = "http://www.plantuml.com/plantuml/png/"
    
    def _connect(self):
        """Conecta ao banco de dados SQLite"""
        conn = sqlite3.connect(self.database_path)
        
        # Adicionar função REGEXP personalizada
        def regexp(expr, item):
            import re
            return re.search(expr, str(item), re.IGNORECASE) is not None
        
        conn.create_function("REGEXP", 2, regexp)
        
        return conn
    
    def get_available_bots(self):
        """
        Recupera lista de bots disponíveis no banco de dados
        
        :return: Lista de nomes de bots únicos
        """
        conn = self._connect()
        cursor = conn.cursor()
        
        # Buscar bots únicos, ordenados alfabeticamente
        cursor.execute("""
            SELECT DISTINCT bot_name 
            FROM chat_history 
            WHERE bot_name IS NOT NULL AND bot_name != ''
            ORDER BY bot_name
        """)
        
        # Extrair nomes dos bots
        bots = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return bots
    
    def extract_text_from_message(self, message):
        """
        Extrai o texto da mensagem, preservando formatação de código e markdown
        
        :param message: Dicionário da mensagem
        :return: Texto extraído com formatação preservada
        """
        # Verificar se a mensagem é um dicionário
        if not isinstance(message, dict):
            return str(message)
        
        # Tentar extrair texto de diferentes formatos de mensagem
        text_candidates = [
            message.get('text', ''),
            message.get('content', ''),
            message.get('message', ''),
            message.get('value', '')
        ]
        
        # Escolher o primeiro candidato não vazio
        text = next((t for t in text_candidates if t), '')
        
        # Renderizar markdown e código
        rendered_text = self.render_message(text)
        
        return rendered_text
    
    def render_message(self, text):
        """
        Renderiza mensagens com suporte avançado a markdown e código
        """
        # Função para processar blocos de código
        def process_code_blocks(text):
            # Padrão para encontrar blocos de código com linguagem
            code_block_pattern = r'```(\w*)\n(.*?)```'
            
            def replace_code_block(match):
                language = match.group(1) or 'text'
                code = match.group(2).strip()
                
                # Garantir que linguagens específicas sejam mapeadas corretamente
                language_map = {
                    'php': 'php',
                    'python': 'python',
                    'js': 'javascript',
                    'javascript': 'javascript',
                    'html': 'html',
                    'css': 'css',
                    'json': 'json',
                    'bash': 'bash',
                    'shell': 'bash'
                }
                
                # Normalizar linguagem
                language = language_map.get(language.lower(), language)
                
                # Escapar HTML para evitar XSS
                escaped_code = html.escape(code)
                
                # Retornar bloco de código formatado
                return f'<pre><code class="language-{language}">{escaped_code}</code></pre>'
            
            return self.re.sub(code_block_pattern, replace_code_block, text, flags=self.re.DOTALL | self.re.MULTILINE)
        
        # Pré-processar blocos de código
        text = process_code_blocks(text)
        
        # Renderizar markdown
        rendered = markdown2.markdown(
            text, 
            extras=[
                'code-friendly', 
                'fenced-code-blocks', 
                'tables', 
                'header-ids', 
                'footnotes', 
                'task-lists'
            ]
        )
        
        # Função para renderizar PlantUML
        def render_plantuml(match):
            uml_code = match.group(1)
            try:
                # Comprimir e codificar o diagrama PlantUML
                compressed = plantuml.deflate_and_encode(uml_code)
                return f'<img src="{self.plantuml_server}{compressed}" alt="PlantUML Diagram"/>'
            except Exception as e:
                return f'<pre>Erro ao renderizar PlantUML: {str(e)}</pre>'
        
        # Substituir blocos PlantUML
        rendered = self.re.sub(
            r'<pre><code class="language-plantuml">(.*?)</code></pre>', 
            render_plantuml, 
            rendered, 
            flags=self.re.DOTALL
        )
        
        # Substituir outros diagramas (mermaid, graphviz, etc.)
        diagram_types = [
            'mermaid', 
            'graphviz', 
            'viz', 
            'dot', 
            'tikz', 
            'wavedrom'
        ]
        
        for diagram_type in diagram_types:
            pattern = fr'<pre><code class="language-{diagram_type}">(.*?)</code></pre>'
            rendered = self.re.sub(
                pattern, 
                lambda m: f'<div class="unsupported-diagram">[Diagrama {diagram_type.upper()} não suportado]</div>', 
                rendered, 
                flags=self.re.DOTALL
            )
        
        return rendered
    
    def search_messages(self, 
                        query: str, 
                        bot_filter: str = None, 
                        page: int = 1, 
                        per_page: int = 20):
        """
        Busca mensagens no banco de dados com suporte a operadores booleanos
        
        :param query: Consulta de busca
        :param bot_filter: Filtro de bot específico
        :param page: Número da página
        :param per_page: Número de resultados por página
        :return: Dicionário com resultados da busca
        """
        # Importar bibliotecas de renderização
        import markdown2
        import html
        import re
        import base64
        import requests
        import plantuml
        
        # Configurar PlantUML
        plantuml_server = "http://www.plantuml.com/plantuml/png/"
        
        # Preparar conexão
        conn = self._connect()
        cursor = conn.cursor()
        
        # Processar a query
        def parse_query(query):
            # Decodificar URL
            import urllib.parse
            query = urllib.parse.unquote(query)
            
            # Separar termos obrigatórios, proibidos e opcionais
            required_terms = []
            forbidden_terms = []
            optional_terms = []
            
            for term in query.split():
                if term.startswith('+'):
                    required_terms.append(term[1:])
                elif term.startswith('-'):
                    forbidden_terms.append(term[1:])
                else:
                    optional_terms.append(term)
            
            return {
                'required': required_terms,
                'forbidden': forbidden_terms,
                'optional': optional_terms
            }
        
        # Construir consulta SQL dinâmica
        parsed_query = parse_query(query)
        
        # Preparar parâmetros e condições
        conditions = []
        params = []
        
        # Filtro de bot, se especificado
        if bot_filter:
            conditions.append("bot_name = ?")
            params.append(bot_filter)
        
        # Adicionar condições para termos obrigatórios
        for term in parsed_query['required']:
            conditions.append("messages REGEXP ?")
            params.append(term)
        
        # Adicionar condições para termos proibidos
        for term in parsed_query['forbidden']:
            conditions.append("messages NOT REGEXP ?")
            params.append(term)
        
        # Adicionar condições para termos opcionais
        optional_conditions = []
        for term in parsed_query['optional']:
            optional_conditions.append("messages REGEXP ?")
            params.append(term)
        
        # Montar consulta base
        base_query = "SELECT bot_name, chat_title, chat_id, messages FROM chat_history"
        
        # Adicionar WHERE se houver condições
        if conditions or optional_conditions:
            base_query += " WHERE "
            
            # Adicionar condições obrigatórias
            if conditions:
                base_query += " AND ".join(conditions)
            
            # Adicionar condições opcionais com OR
            if optional_conditions:
                if conditions:
                    base_query += " AND "
                base_query += "(" + " OR ".join(optional_conditions) + ")"
        
        # Consultas para contagem e resultados
        count_query = f"SELECT COUNT(*) FROM ({base_query})"
        paginated_query = base_query + " LIMIT ? OFFSET ?"
        
        # Adicionar parâmetros de paginação
        params.extend([per_page, (page - 1) * per_page])
        
        try:
            # Executar consulta de contagem
            cursor.execute(count_query, params[:-2])
            total_results = cursor.fetchone()[0]
            
            # Executar consulta paginada
            cursor.execute(paginated_query, params)
            results = cursor.fetchall()
            
            # Processar resultados
            processed_results = []
            for result in results:
                bot_name, chat_title, chat_id, messages_json = result
                try:
                    messages = json.loads(messages_json)
                    
                    # Renderizar mensagens
                    for msg in messages:
                        if 'text' in msg:
                            msg['text'] = self.render_message(msg['text'])
                    
                    # Contar ocorrências do termo de busca
                    occurrences = sum(
                        query.lower() in msg.get('text', '').lower() 
                        for msg in messages
                    )
                    
                    processed_results.append({
                        'bot_name': bot_name,
                        'chat_title': chat_title,
                        'chat_id': chat_id,
                        'messages': messages,
                        'occurrences': occurrences,
                        'view_url': f"/view_chat/{bot_name}/{chat_id}",
                        'original_url': f"https://poe.com/s/chat/{bot_name}/{chat_id}"
                    })
                except json.JSONDecodeError:
                    # Ignorar entradas com JSON inválido
                    continue
            
            # Ordenar resultados por número de ocorrências (decrescente)
            processed_results.sort(key=lambda x: x['occurrences'], reverse=True)
            
            # Calcular total de páginas
            total_pages = (total_results + per_page - 1) // per_page
            
            return {
                'results': processed_results,
                'total_results': total_results,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'query': query
            }
        
        except Exception as e:
            print(f"Erro na busca: {e}")
            return {
                'results': [],
                'total_results': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'query': query
            }
        finally:
            conn.close()

def create_app(database_path):
    """
    Cria aplicação Flask para busca web
    
    :param database_path: Caminho do banco de dados SQLite
    :return: Aplicação Flask
    """
    app = Flask(__name__)
    
    # Desabilitar cache de template para desenvolvimento
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    
    searcher = ChatWebSearcher(database_path)
    
    @app.route('/')
    def index():
        # Buscar bots disponíveis no banco de dados
        bots = searcher.get_available_bots()
        return render_template('index.html', bots=bots)
    
    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('query', '')
        bots = request.args.getlist('bot')  # Múltipla escolha
        page = int(request.args.get('page', 1))
        
        # Se nenhum bot for selecionado, busca em todos
        bot_filter = bots[0] if bots and bots[0] else None
        
        # Realizar busca
        results = searcher.search_messages(
            query, 
            bot_name=bot_filter, 
            page=page
        )
        
        return render_template(
            'results.html', 
            results=results, 
            query=query, 
            selected_bots=bots
        )
    
    @app.route('/chat/<chat_id>')
    def view_chat_detail(chat_id):
        conn = searcher._connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT messages, bot_name, chat_title FROM chat_history WHERE chat_id = ?", 
            (chat_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            messages_json, bot_name, chat_title = result
            messages = json.loads(messages_json)
            
            # Formatar mensagens para exibição
            formatted_messages = []
            for msg in messages:
                # Extrair texto usando o método do SearchEngine
                text = searcher.extract_text_from_message(msg)
                
                # Preservar outras informações originais
                formatted_msg = {
                    'text': text,
                    'original': msg
                }
                formatted_messages.append(formatted_msg)
            
            formatted_json = highlight(
                json.dumps(messages, indent=2),
                JsonLexer(),
                HtmlFormatter(style='monokai')
            )
            
            # Adicionar timestamp de renderização para debug
            render_timestamp = datetime.now().isoformat()
            
            return render_template(
                'chat_detail.html', 
                messages=formatted_messages, 
                formatted_json=formatted_json,
                bot_name=bot_name,
                chat_title=chat_title,
                render_timestamp=render_timestamp  # Novo campo para debug
            )
        
        return "Chat não encontrado", 404
    
    @app.route('/view_chat/<bot_name>/<chat_id>')
    def view_chat(bot_name, chat_id):
        """
        Renderiza o chat completo a partir dos dados do SQLite
        """
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Buscar mensagens do chat específico
        cursor.execute(
            "SELECT messages, bot_name, chat_title FROM chat_history WHERE bot_name = ? AND chat_id = ?", 
            (bot_name, chat_id)
        )
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return "Chat não encontrado", 404
        
        # Carregar mensagens
        messages_json, bot_name, chat_title = result
        messages = json.loads(messages_json)
        
        return render_template(
            'view_chat.html', 
            bot_name=bot_name, 
            chat_title=chat_title,
            messages=messages
        )
    
    return app

def main():
    """
    Ponto de entrada para execução do chat web search
    Suporta modos de desenvolvimento e produção
    """
    import argparse
    import os
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Chat Web Search')
    parser.add_argument(
        '--dev', 
        action='store_true', 
        help='Executar em modo de desenvolvimento'
    )
    parser.add_argument(
        '--database', 
        default='historico.sqlite', 
        help='Caminho do banco de dados SQLite'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000, 
        help='Porta para o servidor web'
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Criar aplicação Flask
    app = create_app(args.database)
    
    # Configurações de execução
    if args.dev:
        # Modo de desenvolvimento
        app.config['DEBUG'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        # Habilitar recarregamento automático
        try:
            from flask_cors import CORS
            CORS(app)  # Permitir CORS em desenvolvimento
        except ImportError:
            print("CORS não instalado. Instale com: pip install flask-cors")
        
        # Executar em modo de desenvolvimento
        app.run(
            host='0.0.0.0', 
            port=args.port, 
            debug=True, 
            use_reloader=True
        )
    else:
        # Modo de produção
        return app

if __name__ == '__main__':
    main()
