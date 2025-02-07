import os
import json
import sqlite3
import argparse
from typing import List, Dict, Any
from flask import Flask, render_template, request, jsonify
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

class ChatWebSearcher:
    def __init__(self, database_path: str):
        """
        Inicializa o buscador web de chats
        
        :param database_path: Caminho para o banco de dados SQLite
        """
        self.database_path = os.path.abspath(database_path)
        
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Banco de dados {self.database_path} não existe.")
    
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
        Extrai texto de diferentes formatos de mensagem.
        
        :param message: Mensagem em diferentes formatos
        :return: Texto extraído ou string vazia
        """
        # Se já for uma string, retorna diretamente
        if isinstance(message, str):
            return message
        
        # Se for um dicionário, tentar extrair texto de diferentes campos
        if isinstance(message, dict):
            # Priorizar campos de texto conhecidos
            text_fields = [
                'text', 
                'content', 
                'message', 
                'body', 
                'description'
            ]
            
            for field in text_fields:
                if field in message:
                    # Se o campo for um dicionário, tentar extrair texto
                    if isinstance(message[field], dict):
                        # Tentar campos aninhados
                        for subfield in ['text', 'content', 'value']:
                            if subfield in message[field]:
                                return str(message[field][subfield])
                    
                    # Se não for dicionário, converter para string
                    return str(message[field])
        
        # Se não conseguir extrair, converter para string
        return str(message)
    
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
                    processed_results.append({
                        'bot_name': bot_name,
                        'chat_title': chat_title,
                        'chat_id': chat_id,
                        'messages': messages
                    })
                except json.JSONDecodeError:
                    # Ignorar entradas com JSON inválido
                    continue
            
            # Calcular total de páginas
            total_pages = (total_results + per_page - 1) // per_page
            
            return {
                'results': processed_results,
                'total_results': total_results,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        
        except Exception as e:
            print(f"Erro na busca: {e}")
            return {
                'results': [],
                'total_results': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
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
        
        results = searcher.search_messages(query, bot_filter, page)
        
        # Buscar bots disponíveis novamente para manter o filtro
        available_bots = searcher.get_available_bots()
        
        # Formatar resultados para template
        for result in results['results']:
            result['formatted_json'] = highlight(
                json.dumps(result['messages'], indent=2),
                JsonLexer(),
                HtmlFormatter(style='monokai')
            )
        
        return render_template(
            'results.html', 
            results=results, 
            query=query, 
            selected_bots=bots,
            available_bots=available_bots
        )
    
    @app.route('/chat/<chat_id>')
    def view_chat(chat_id):
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
            return render_template(
                'chat_detail.html', 
                messages=formatted_messages, 
                formatted_json=formatted_json,
                bot_name=bot_name,
                chat_title=chat_title
            )
        
        return "Chat não encontrado", 404
    
    return app

def main():
    parser = argparse.ArgumentParser(description='Iniciar servidor de busca de chats')
    parser.add_argument(
        '-d', 
        '--database', 
        default=os.path.join('historico', 'historico.sqlite'),
        help='Caminho para o banco de dados SQLite'
    )
    
    args = parser.parse_args()
    
    # Garantir que o caminho seja absoluto
    database_path = os.path.abspath(args.database)
    
    app = create_app(database_path)
    app.run(debug=True)

if __name__ == '__main__':
    main()
