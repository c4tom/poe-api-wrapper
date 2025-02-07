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
        return sqlite3.connect(self.database_path)
    
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
                        bot_name: str = None, 
                        page: int = 1, 
                        per_page: int = 100):
        """
        Busca mensagens no banco de dados com paginação
        
        :param query: Texto de busca
        :param bot_name: Nome do bot para filtrar (opcional)
        :param page: Página atual
        :param per_page: Registros por página
        :return: Dicionário com resultados e metadados
        """
        import re

        conn = self._connect()
        cursor = conn.cursor()
        
        # Preparar condições de busca
        conditions = []
        params = []
        
        # Filtro por bot, se especificado
        if bot_name:
            conditions.append("bot_name = ?")
            params.append(bot_name)
        
        # Verificar se é uma expressão regular
        is_regex = False
        try:
            re.compile(query)
            is_regex = True
        except re.error:
            is_regex = False
        
        # Definir estratégia de busca
        if is_regex:
            # Busca por expressão regular
            conditions.append("messages REGEXP ?")
            params.append(query)
        else:
            # Busca por texto simples
            conditions.append("messages LIKE ?")
            params.append(f"%{query}%")
        
        # Construir consulta SQL base
        base_query = """
        SELECT id, bot_name, chat_title, chat_id, messages 
        FROM chat_history
        """
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        # Consulta para total de resultados
        count_query = f"SELECT COUNT(*) FROM ({base_query}) as subquery"
        cursor.execute(count_query, params)
        total_results = cursor.fetchone()[0]
        
        # Calcular paginação
        offset = (page - 1) * per_page
        paginated_query = base_query + " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        # Executar consulta paginada
        cursor.execute(paginated_query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Processar resultados
        processed_results = []
        for result in results:
            _, bot_name, chat_title, chat_id, messages_json = result
            
            try:
                messages = json.loads(messages_json)
                
                # Encontrar trechos com a palavra
                matching_messages = []
                for msg in messages:
                    text = self.extract_text_from_message(msg)
                    
                    # Verificar se texto corresponde à busca
                    if is_regex:
                        if re.search(query, text, re.IGNORECASE):
                            matching_messages.append(msg)
                    else:
                        if query.lower() in text.lower():
                            matching_messages.append(msg)
                
                processed_results.append({
                    'bot_name': bot_name,
                    'chat_title': chat_title,
                    'chat_id': chat_id,
                    'matching_messages': matching_messages,
                    'total_matching': len(matching_messages)
                })
            except Exception as e:
                print(f"Erro ao processar mensagens: {e}")
        
        return {
            'results': processed_results,
            'total_results': total_results,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_results + per_page - 1) // per_page
        }

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
                json.dumps(result['matching_messages'], indent=2),
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
    parser = argparse.ArgumentParser(description='Servidor web de busca de chats')
    parser.add_argument('database', help='Caminho do banco de dados SQLite')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Porta do servidor')
    parser.add_argument('--host', default='0.0.0.0', help='Host do servidor')
    
    args = parser.parse_args()
    
    app = create_app(args.database)
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == '__main__':
    main()
