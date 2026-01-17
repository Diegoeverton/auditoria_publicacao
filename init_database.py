"""
Script de Inicialização do Banco de Dados
Cria o banco de dados e as tabelas necessárias
"""
import sys
from pathlib import Path
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager


def criar_banco_dados():
    """Cria o banco de dados se não existir"""
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
    
    db_name = os.getenv('DB_NAME', 'auditoria_publicacao')
    
    try:
        # Conecta sem especificar banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Cria banco se não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Banco de dados '{db_name}' criado/verificado")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"✗ Erro ao criar banco de dados: {e}")
        return False


def main():
    print("=" * 70)
    print("INICIALIZAÇÃO DO BANCO DE DADOS")
    print("=" * 70)
    
    # Verificar configurações
    print("\n[1/4] Verificando configurações...")
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'auditoria_publicacao')
    db_user = os.getenv('DB_USER', 'root')
    
    print(f"  Host: {db_host}")
    print(f"  Porta: {db_port}")
    print(f"  Banco: {db_name}")
    print(f"  Usuário: {db_user}")
    
    if not os.getenv('DB_PASSWORD'):
        print("\n⚠ Aviso: DB_PASSWORD não está definido no .env")
        print("  Se o MySQL exigir senha, configure no arquivo .env")
    
    # Criar banco de dados
    print("\n[2/4] Criando banco de dados...")
    if not criar_banco_dados():
        print("\n✗ Falha ao criar banco de dados")
        print("\nVerifique:")
        print("  1. MySQL está instalado e rodando")
        print("  2. Credenciais no .env estão corretas")
        print("  3. Usuário tem permissão para criar bancos")
        return 1
    
    # Criar tabelas
    print("\n[3/4] Criando tabelas...")
    db = DatabaseManager()
    
    if not db.connect():
        print("\n✗ Falha ao conectar ao banco")
        return 1
    
    if not db.create_tables():
        print("\n✗ Falha ao criar tabelas")
        db.disconnect()
        return 1
    
    # Verificar estrutura
    print("\n[4/4] Verificando estrutura...")
    stats = db.get_estatisticas()
    print(f"  ✓ Tabelas criadas e funcionando")
    print(f"  Total de registros: {stats.get('total_fasciculos', 0)} fascículos")
    
    db.disconnect()
    
    print("\n" + "=" * 70)
    print("✓ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
    print("=" * 70)
    print("\nPróximos passos:")
    print("  1. O sistema agora salvará logs no MySQL automaticamente")
    print("  2. Use os scripts normalmente (main.py, send_system.py, etc.)")
    print("  3. Consulte logs com: python consultar_db.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
