import os
import json
import sqlite3
import argparse
import sys
from typing import List, Dict
from rich.console import Console
from rich.table import Table
import hashlib

def convert_to_sqlite(directory: str, output_db: str = None):
    """
    Converte arquivos JSON de histórico de chat para um banco de dados SQLite.
    
    :param directory: Diretório contendo os arquivos JSON de histórico
    :param output_db: Caminho do banco de dados SQLite de saída
    """
    console = Console()
    
    # Garantir caminho absoluto para o diretório
    directory = os.path.abspath(directory)
    
    # Se nenhum banco de dados for especificado, use o padrão
    if not output_db:
        output_db = os.path.join(directory, 'chat_history.sqlite')
    else:
        # Adicionar extensão .sqlite se não existir
        if not output_db.lower().endswith('.sqlite'):
            output_db += '.sqlite'
        
        # Garantir caminho absoluto para o banco de dados
        output_db = os.path.abspath(output_db)
    
    # Garantir que o diretório de saída existe
    os.makedirs(os.path.dirname(output_db), exist_ok=True)
    
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()
    
    # Criar tabela de histórico de chat
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_name TEXT,
        chat_title TEXT,
        chat_id TEXT,
        messages TEXT
    )
    ''')
    
    # Contador de arquivos processados
    total_files = 0
    total_chats = 0
    processed_files = []
    skipped_files = []
    
    # Percorrer diretórios recursivamente
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                total_files += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Tentar diferentes estratégias de leitura
                        try:
                            chat_data = json.load(f)
                        except json.JSONDecodeError:
                            # Tentar ler como lista
                            f.seek(0)
                            chat_data = json.loads(f.read())
                    
                    # Verificar se o JSON tem conteúdo
                    if not chat_data:
                        skipped_files.append(f"{file_path}: JSON vazio")
                        continue
                    
                    # Normalizar dados se for uma lista
                    if isinstance(chat_data, list):
                        # Tentar extrair informações da lista de mensagens
                        messages = chat_data
                        bot_name = os.path.basename(os.path.dirname(file_path))
                        chat_title = os.path.splitext(file)[0]
                        
                        # Gerar chat_id consistente
                        chat_id = hashlib.md5(
                            (file_path + str(len(messages))).encode()
                        ).hexdigest()
                    else:
                        # Extrair informações do nome do arquivo ou do JSON
                        bot_name = os.path.basename(os.path.dirname(file_path))
                        
                        chat_title = (
                            chat_data.get('chat_title') or 
                            chat_data.get('title') or 
                            os.path.splitext(file)[0]
                        )
                        
                        # Tentar obter chat_id de diferentes formas
                        chat_id = (
                            chat_data.get('chat_id') or 
                            chat_data.get('id') or 
                            hashlib.md5(
                                (file_path + chat_title).encode()
                            ).hexdigest()
                        )
                        
                        # Extrair mensagens de diferentes estruturas
                        messages = chat_data.get('messages')
                        if not messages:
                            # Se não encontrar messages, tentar usar o JSON inteiro
                            messages = chat_data
                    
                    # Converter para JSON string
                    messages_json = json.dumps(messages, ensure_ascii=False)
                    
                    # Inserir no banco de dados
                    cursor.execute('''
                    INSERT OR REPLACE INTO chat_history 
                    (bot_name, chat_title, chat_id, messages) 
                    VALUES (?, ?, ?, ?)
                    ''', (bot_name, chat_title, chat_id, messages_json))
                    
                    total_chats += 1
                    processed_files.append(file_path)
                    
                except Exception as e:
                    skipped_files.append(f"{file_path}: {str(e)}")
    
    # Commit e fechar conexão
    conn.commit()
    conn.close()
    
    # Relatório final
    console.print(f"\n[green]Conversão concluída:[/green]")
    console.print(f"Total de arquivos: {total_files}")
    console.print(f"Chats salvos: {total_chats}")
    console.print(f"Banco de dados: {output_db}")
    
    # Detalhes de depuração
    console.print("\n[yellow]Arquivos processados:[/yellow]")
    for file in processed_files[:10]:  # Mostrar primeiros 10
        console.print(f"  ✓ {file}")
    
    if len(processed_files) > 10:
        console.print(f"  ... e mais {len(processed_files) - 10}")
    
    # Arquivos com erro
    if skipped_files:
        console.print("\n[red]Arquivos com problema:[/red]")
        for file in skipped_files[:10]:  # Mostrar primeiros 10
            console.print(f"  ✗ {file}")
        
        if len(skipped_files) > 10:
            console.print(f"  ... e mais {len(skipped_files) - 10}")
    
    return total_chats

def main():
    parser = argparse.ArgumentParser(description='Converte histórico de chats para SQLite')
    parser.add_argument('directory', help='Diretório contendo os arquivos JSON de histórico')
    parser.add_argument('-o', '--output', help='Caminho do banco de dados SQLite de saída')
    
    args = parser.parse_args()
    
    convert_to_sqlite(args.directory, args.output)

if __name__ == '__main__':
    main()
