"""
Sistema Principal - Geração de Hash para Fascículos
Este script gera hashes criptografados para fascículos e registra na blockchain
"""
import sys
import argparse
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from hash_generator import HashGenerator
from crypto_manager import CryptoManager
from blockchain_audit import BlockchainAudit, BlockType
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH
import json


def main():
    parser = argparse.ArgumentParser(
        description='Gera hash criptografado para um fascículo e registra na blockchain'
    )
    parser.add_argument('--edicao', required=True, help='Nome ou número da edição')
    parser.add_argument('--fasciculo', required=True, help='Nome ou número do fascículo')
    parser.add_argument('--pdf', required=True, help='Caminho para o arquivo PDF do fascículo')
    parser.add_argument('--metadata', help='Metadados adicionais em formato JSON', default='{}')
    
    args = parser.parse_args()
    
    # Valida arquivo PDF
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"✗ Erro: Arquivo PDF não encontrado: {pdf_path}")
        return 1
    
    if pdf_path.suffix.lower() != '.pdf':
        print(f"✗ Erro: O arquivo deve ser um PDF")
        return 1
    
    # Parse metadata
    try:
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError:
        print(f"✗ Erro: Metadados inválidos. Use formato JSON válido")
        return 1
    
    print("=" * 70)
    print("SISTEMA DE GERAÇÃO DE HASH PARA FASCÍCULOS")
    print("=" * 70)
    print(f"\nEdição: {args.edicao}")
    print(f"Fascículo: {args.fasciculo}")
    print(f"PDF: {pdf_path}")
    print(f"Tamanho: {pdf_path.stat().st_size / 1024:.2f} KB")
    
    # Inicializa componentes
    print("\n[1/5] Inicializando componentes...")
    hash_gen = HashGenerator()
    crypto = CryptoManager(ENCRYPTION_KEY_PATH)
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    
    # Gera hash do fascículo
    print("[2/5] Gerando hash do fascículo...")
    hash_info = hash_gen.generate_fasciculo_hash(
        pdf_path=pdf_path,
        edicao=args.edicao,
        fasciculo=args.fasciculo,
        metadata=metadata
    )
    
    print(f"  ✓ Hash ID: {hash_info['hash_id']}")
    print(f"  ✓ Hash do Fascículo: {hash_info['fasciculo_hash'][:32]}...")
    
    # Registra geração na blockchain
    print("[3/5] Registrando geração na blockchain...")
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': args.edicao,
            'fasciculo': args.fasciculo,
            'fasciculo_hash': hash_info['fasciculo_hash'],
            'pdf_path': str(pdf_path),
            'pdf_size': hash_info['pdf_size'],
            'action': 'Hash gerado para fascículo'
        },
        block_type=BlockType.HASH_GENERATED
    )
    print(f"  ✓ Bloco adicionado à blockchain")
    
    # Criptografa informações
    print("[4/5] Criptografando informações sensíveis...")
    encrypted_info = crypto.encrypt_hash(hash_info)
    print(f"  ✓ Dados criptografados")
    
    # Registra criptografia na blockchain
    print("[5/5] Registrando criptografia na blockchain...")
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': args.edicao,
            'fasciculo': args.fasciculo,
            'encrypted_data_length': len(encrypted_info['encrypted_data']),
            'action': 'Hash criptografado'
        },
        block_type=BlockType.HASH_ENCRYPTED
    )
    print(f"  ✓ Bloco de criptografia adicionado")
    
    # Salva informações criptografadas em arquivo
    output_file = Path('data') / f"hash_{hash_info['hash_id']}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(encrypted_info, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("✓ HASH GERADO E REGISTRADO COM SUCESSO!")
    print("=" * 70)
    print(f"\nHash ID: {hash_info['hash_id']}")
    print(f"Arquivo de hash: {output_file}")
    print(f"\nPara enviar este fascículo, use:")
    print(f"  python send_system.py --hash-id {hash_info['hash_id']} --destinatario email@exemplo.com")
    print(f"\nPara consultar a auditoria, use:")
    print(f"  python audit_query.py --hash-id {hash_info['hash_id']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
