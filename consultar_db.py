"""
Script de Consulta ao Banco de Dados
Consulta logs e hashes armazenados no MySQL
"""
import sys
from pathlib import Path
import argparse
from datetime import datetime
from tabulate import tabulate
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager


def consultar_fasciculo(db: DatabaseManager, hash_id: str):
    """Consulta informações de um fascículo específico"""
    print("=" * 70)
    print(f"INFORMAÇÕES DO FASCÍCULO - Hash ID: {hash_id}")
    print("=" * 70)
    
    # Buscar fascículo
    fasciculo = db.buscar_fasciculo(hash_id)
    
    if not fasciculo:
        print(f"\n✗ Fascículo não encontrado: {hash_id}")
        return
    
    # Mostrar informações
    print(f"\nEdição: {fasciculo['edicao']}")
    print(f"Fascículo: {fasciculo['fasciculo']}")
    print(f"Hash: {fasciculo['fasciculo_hash'][:32]}...")
    print(f"PDF: {fasciculo['pdf_path']}")
    print(f"Tamanho: {fasciculo['pdf_size'] / 1024:.2f} KB")
    print(f"Criado em: {fasciculo['created_at']}")
    
    # Buscar logs
    logs = db.buscar_logs_fasciculo(hash_id)
    
    if logs:
        print(f"\n{'-' * 70}")
        print(f"HISTÓRICO DE EVENTOS ({len(logs)} eventos)")
        print(f"{'-' * 70}")
        
        table_data = []
        for log in logs:
            table_data.append([
                log['id'],
                log['created_at'].strftime('%d/%m/%Y %H:%M:%S'),
                log['evento_tipo'],
                log['destinatario'] or '-'
            ])
        
        headers = ['ID', 'Data/Hora', 'Evento', 'Destinatário']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))


def consultar_edicao(db: DatabaseManager, edicao: str):
    """Consulta todos os fascículos de uma edição"""
    print("=" * 70)
    print(f"FASCÍCULOS DA EDIÇÃO: {edicao}")
    print("=" * 70)
    
    fasciculos = db.buscar_fasciculos_edicao(edicao)
    
    if not fasciculos:
        print(f"\n✗ Nenhum fascículo encontrado para a edição: {edicao}")
        return
    
    print(f"\nTotal de fascículos: {len(fasciculos)}\n")
    
    table_data = []
    for f in fasciculos:
        # Buscar se foi enviado
        logs = db.buscar_logs_fasciculo(f['hash_id'])
        enviado = any(log['evento_tipo'] == 'EMAIL_SENT' for log in logs)
        status = '✓ Enviado' if enviado else '⏳ Pendente'
        
        table_data.append([
            f['fasciculo'],
            f['hash_id'][:16] + '...',
            f['created_at'].strftime('%d/%m/%Y %H:%M'),
            len(logs),
            status
        ])
    
    headers = ['Fascículo', 'Hash ID', 'Criado em', 'Eventos', 'Status']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def mostrar_estatisticas(db: DatabaseManager):
    """Mostra estatísticas gerais do banco"""
    print("=" * 70)
    print("ESTATÍSTICAS DO BANCO DE DADOS")
    print("=" * 70)
    
    stats = db.get_estatisticas()
    
    print(f"\nTotal de fascículos: {stats.get('total_fasciculos', 0)}")
    print(f"Total de edições: {stats.get('total_edicoes', 0)}")
    print(f"Total de emails enviados: {stats.get('total_emails_enviados', 0)}")
    print(f"Total de logs: {stats.get('total_logs', 0)}")
    
    if stats.get('logs_por_tipo'):
        print("\nLogs por tipo:")
        for tipo, total in stats['logs_por_tipo'].items():
            print(f"  {tipo}: {total}")


def listar_ultimos(db: DatabaseManager, limite: int = 10):
    """Lista os últimos fascículos criados"""
    print("=" * 70)
    print(f"ÚLTIMOS {limite} FASCÍCULOS CRIADOS")
    print("=" * 70)
    
    if not db.connection or not db.connection.is_connected():
        if not db.connect():
            return
    
    cursor = db.connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT hash_id, edicao, fasciculo, created_at 
            FROM fasciculos 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        cursor.execute(query, (limite,))
        fasciculos = cursor.fetchall()
        
        if not fasciculos:
            print("\nNenhum fascículo encontrado")
            return
        
        print(f"\nTotal: {len(fasciculos)}\n")
        
        table_data = []
        for f in fasciculos:
            table_data.append([
                f['edicao'],
                f['fasciculo'],
                f['hash_id'][:16] + '...',
                f['created_at'].strftime('%d/%m/%Y %H:%M:%S')
            ])
        
        headers = ['Edição', 'Fascículo', 'Hash ID', 'Criado em']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(
        description='Consulta logs e hashes no banco de dados MySQL'
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--hash-id', help='Consulta por Hash ID do fascículo')
    group.add_argument('--edicao', help='Consulta todos os fascículos de uma edição')
    group.add_argument('--estatisticas', action='store_true',
                      help='Mostra estatísticas gerais')
    group.add_argument('--ultimos', type=int, metavar='N',
                      help='Lista os últimos N fascículos criados')
    
    args = parser.parse_args()
    
    # Conectar ao banco
    db = DatabaseManager()
    
    if not db.connect():
        print("\n✗ Erro ao conectar ao banco de dados")
        print("\nVerifique:")
        print("  1. MySQL está rodando")
        print("  2. Arquivo .env está configurado")
        print("  3. Banco foi inicializado: python init_database.py")
        return 1
    
    try:
        # Executar consulta apropriada
        if args.hash_id:
            consultar_fasciculo(db, args.hash_id)
        elif args.edicao:
            consultar_edicao(db, args.edicao)
        elif args.estatisticas:
            mostrar_estatisticas(db)
        elif args.ultimos:
            listar_ultimos(db, args.ultimos)
    
    finally:
        db.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
