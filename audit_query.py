"""
Sistema de Consulta de Auditoria
Consulta e verifica a trilha de auditoria na blockchain
"""
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from blockchain_audit import BlockchainAudit, BlockType
from config import BLOCKCHAIN_PATH
from tabulate import tabulate


def format_timestamp(iso_timestamp: str) -> str:
    """Formata timestamp ISO para formato legível"""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return iso_timestamp


def query_by_hash_id(blockchain: BlockchainAudit, hash_id: str):
    """Consulta trilha de auditoria por hash_id"""
    print("=" * 70)
    print(f"TRILHA DE AUDITORIA - Hash ID: {hash_id}")
    print("=" * 70)
    
    trail = blockchain.get_audit_trail(hash_id)
    
    if not trail:
        print(f"\n✗ Nenhum registro encontrado para o hash_id: {hash_id}")
        return
    
    # Informações gerais
    first_event = trail[0]
    print(f"\nEdição: {first_event['data'].get('edicao', 'N/A')}")
    print(f"Fascículo: {first_event['data'].get('fasciculo', 'N/A')}")
    print(f"Total de eventos: {len(trail)}")
    
    # Tabela de eventos
    print("\n" + "-" * 70)
    print("EVENTOS NA TRILHA DE AUDITORIA")
    print("-" * 70)
    
    table_data = []
    for event in trail:
        table_data.append([
            event['block_index'],
            format_timestamp(event['timestamp']),
            event['action'],
            event['data'].get('destinatario', '-')
        ])
    
    headers = ['Bloco', 'Data/Hora', 'Ação', 'Destinatário']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Detalhes do último evento
    last_event = trail[-1]
    print("\n" + "-" * 70)
    print("DETALHES DO ÚLTIMO EVENTO")
    print("-" * 70)
    print(f"Ação: {last_event['action']}")
    print(f"Data/Hora: {format_timestamp(last_event['timestamp'])}")
    print(f"Hash do Bloco: {last_event['block_hash']}")
    
    if 'fasciculo_hash' in last_event['data']:
        print(f"Hash do Fascículo: {last_event['data']['fasciculo_hash']}")
    
    if 'destinatario' in last_event['data']:
        print(f"Destinatário: {last_event['data']['destinatario']}")


def query_by_edicao(blockchain: BlockchainAudit, edicao: str):
    """Consulta todos os fascículos de uma edição"""
    print("=" * 70)
    print(f"FASCÍCULOS DA EDIÇÃO: {edicao}")
    print("=" * 70)
    
    blocks = blockchain.get_blocks_by_edicao(edicao)
    
    if not blocks:
        print(f"\n✗ Nenhum registro encontrado para a edição: {edicao}")
        return
    
    # Agrupa por hash_id
    fasciculos = {}
    for block in blocks:
        hash_id = block.data.get('hash_id')
        if hash_id:
            if hash_id not in fasciculos:
                fasciculos[hash_id] = {
                    'fasciculo': block.data.get('fasciculo', 'N/A'),
                    'hash_id': hash_id,
                    'eventos': []
                }
            fasciculos[hash_id]['eventos'].append(block.block_type)
    
    # Tabela de fascículos
    table_data = []
    for hash_id, info in fasciculos.items():
        status = '✓ Enviado' if BlockType.EMAIL_SENT.value in info['eventos'] else '⏳ Pendente'
        table_data.append([
            info['fasciculo'],
            hash_id[:16] + '...',
            len(info['eventos']),
            status
        ])
    
    headers = ['Fascículo', 'Hash ID', 'Eventos', 'Status']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    print(f"\nTotal de fascículos: {len(fasciculos)}")


def verify_integrity(blockchain: BlockchainAudit):
    """Verifica integridade da blockchain"""
    print("=" * 70)
    print("VERIFICAÇÃO DE INTEGRIDADE DA BLOCKCHAIN")
    print("=" * 70)
    
    print(f"\nTotal de blocos: {len(blockchain.chain)}")
    print("\nVerificando integridade...")
    
    is_valid = blockchain.verify_integrity()
    
    if is_valid:
        print("\n✓ BLOCKCHAIN ÍNTEGRA")
        print("  Todos os blocos estão válidos e a cadeia está intacta")
    else:
        print("\n✗ BLOCKCHAIN COMPROMETIDA")
        print("  Foram detectadas inconsistências na cadeia")
    
    return is_valid


def show_statistics(blockchain: BlockchainAudit):
    """Mostra estatísticas da blockchain"""
    print("=" * 70)
    print("ESTATÍSTICAS DA BLOCKCHAIN")
    print("=" * 70)
    
    stats = blockchain.get_statistics()
    
    print(f"\nTotal de blocos: {stats['total_blocks']}")
    print(f"Total de edições: {stats['total_edicoes']}")
    print(f"Total de fascículos: {stats['total_fasciculos']}")
    print(f"Total de emails enviados: {stats['total_emails_sent']}")
    
    print("\nBlocos por tipo:")
    for block_type, count in stats['blocks_by_type'].items():
        print(f"  {block_type}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description='Consulta e verifica a trilha de auditoria na blockchain'
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--hash-id', help='Consulta por Hash ID do fascículo')
    group.add_argument('--edicao', help='Consulta todos os fascículos de uma edição')
    group.add_argument('--verificar-integridade', action='store_true',
                      help='Verifica integridade da blockchain')
    group.add_argument('--estatisticas', action='store_true',
                      help='Mostra estatísticas da blockchain')
    
    args = parser.parse_args()
    
    # Inicializa blockchain
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    
    # Executa consulta apropriada
    if args.hash_id:
        query_by_hash_id(blockchain, args.hash_id)
    elif args.edicao:
        query_by_edicao(blockchain, args.edicao)
    elif args.verificar_integridade:
        is_valid = verify_integrity(blockchain)
        return 0 if is_valid else 1
    elif args.estatisticas:
        show_statistics(blockchain)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
