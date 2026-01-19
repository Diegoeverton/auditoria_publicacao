"""
Script de Demonstração
Demonstra o funcionamento completo do sistema sem necessidade de email real
"""
import sys
from pathlib import Path
import json

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from hash_generator import HashGenerator
from crypto_manager import CryptoManager
from blockchain_audit import BlockchainAudit, BlockType
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH


def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_step(step_num, total_steps, description):
    """Imprime passo formatado"""
    print(f"[{step_num}/{total_steps}] {description}")


def main():
    print_header("DEMONSTRAÇÃO DO SISTEMA DE AUDITORIA DE PUBLICAÇÃO")
    
    print("Este script demonstra o fluxo completo do sistema:")
    print("  1. Geração de hash para um fascículo")
    print("  2. Criptografia das informações")
    print("  3. Registro na blockchain")
    print("  4. Descriptografia")
    print("  5. Simulação de envio")
    print("  6. Consulta de auditoria")
    print("  7. Verificação de integridade")
    
    input("\nPressione ENTER para continuar...")
    
    # Inicializa componentes
    print_header("INICIALIZAÇÃO DOS COMPONENTES")
    
    print_step(1, 7, "Inicializando Hash Generator...")
    hash_gen = HashGenerator()
    print("  [OK] Hash Generator inicializado")
    
    print_step(2, 7, "Inicializando Crypto Manager...")
    crypto = CryptoManager(ENCRYPTION_KEY_PATH)
    print("  [OK] Crypto Manager inicializado")
    
    print_step(3, 7, "Inicializando Blockchain...")
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    print(f"  [OK] Blockchain inicializada com {len(blockchain.chain)} blocos")
    
    # Simula geração de hash para um fascículo
    print_header("GERAÇÃO DE HASH PARA FASCÍCULO")
    
    # Cria um PDF de demonstração se não existir
    demo_pdf_path = Path('fasciculos') / 'demo_fasciculo.pdf'
    demo_pdf_path.parent.mkdir(exist_ok=True)
    
    if not demo_pdf_path.exists():
        print("  Criando PDF de demonstração...")
        # Cria um PDF simples para demonstração
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(str(demo_pdf_path), pagesize=letter)
            c.drawString(100, 750, "FASCÍCULO DE DEMONSTRAÇÃO")
            c.drawString(100, 730, "Edição: Demo 001")
            c.drawString(100, 710, "Fascículo: 01")
            c.drawString(100, 680, "Este é um PDF de demonstração para o sistema de auditoria.")
            c.save()
            print("  [OK] PDF de demonstração criado")
        except ImportError:
            # Se reportlab não estiver disponível, cria um arquivo vazio
            demo_pdf_path.write_bytes(b'%PDF-1.4\n%Demo PDF\n')
            print("  [OK] PDF de demonstração criado (simplificado)")
    
    print_step(4, 7, "Gerando hash do fascículo...")
    
    # Dados do fascículo
    edicao = "Demo 001"
    fasciculo = "Fascículo 01"
    
    # Gera hash (se o PDF não for válido, usará hash do arquivo binário)
    try:
        hash_info = hash_gen.generate_fasciculo_hash(
            pdf_path=demo_pdf_path,
            edicao=edicao,
            fasciculo=fasciculo,
            metadata={'demo': True, 'versao': '1.0'}
        )
    except Exception as e:
        print(f"  [AVISO] Aviso: {e}")
        print("  Usando hash simulado para demonstração...")
        import hashlib
        import uuid
        hash_info = {
            'hash_id': str(uuid.uuid4()),
            'fasciculo_hash': hashlib.sha256(b"demo").hexdigest(),
            'edicao': edicao,
            'fasciculo': fasciculo,
            'pdf_path': str(demo_pdf_path),
            'pdf_size': demo_pdf_path.stat().st_size if demo_pdf_path.exists() else 0,
            'pdf_metadata': {},
            'timestamp': '2026-01-12T19:00:00',
            'algorithm': 'sha256',
            'metadata': {'demo': True}
        }
    
    print(f"  [OK] Hash ID: {hash_info['hash_id']}")
    print(f"  [OK] Hash: {hash_info['fasciculo_hash'][:32]}...")
    
    # Registra na blockchain
    print_step(5, 7, "Registrando na blockchain...")
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': edicao,
            'fasciculo': fasciculo,
            'fasciculo_hash': hash_info['fasciculo_hash'],
            'pdf_path': str(demo_pdf_path),
            'action': 'Hash gerado para fascículo (DEMO)'
        },
        block_type=BlockType.HASH_GENERATED
    )
    print("  [OK] Bloco HASH_GENERATED adicionado")
    
    # Criptografa
    print_header("CRIPTOGRAFIA")
    
    print_step(6, 7, "Criptografando informações sensíveis...")
    encrypted_info = crypto.encrypt_hash(hash_info)
    print(f"  [OK] Dados criptografados ({len(encrypted_info['encrypted_data'])} chars)")
    
    # Registra criptografia
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': edicao,
            'fasciculo': fasciculo,
            'action': 'Hash criptografado (DEMO)'
        },
        block_type=BlockType.HASH_ENCRYPTED
    )
    print("  [OK] Bloco HASH_ENCRYPTED adicionado")
    
    # Descriptografa
    print_header("DESCRIPTOGRAFIA E ENVIO")
    
    print_step(7, 7, "Descriptografando informações...")
    decrypted_info = crypto.decrypt_hash(encrypted_info)
    print(f"  [OK] Hash descriptografado: {decrypted_info['fasciculo_hash'][:32]}...")
    
    # Registra descriptografia
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': edicao,
            'fasciculo': fasciculo,
            'destinatario': 'demo@exemplo.com',
            'action': 'Hash descriptografado para envio (DEMO)'
        },
        block_type=BlockType.HASH_DECRYPTED
    )
    print("  [OK] Bloco HASH_DECRYPTED adicionado")
    
    # Simula envio
    print("\n  Simulando envio de email...")
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': edicao,
            'fasciculo': fasciculo,
            'destinatario': 'demo@exemplo.com',
            'fasciculo_hash': decrypted_info['fasciculo_hash'],
            'action': 'Fascículo enviado (DEMO)'
        },
        block_type=BlockType.EMAIL_SENT
    )
    print("  [OK] Bloco EMAIL_SENT adicionado")
    print("  [OK] Email simulado enviado para: demo@exemplo.com")
    
    # Consulta auditoria
    print_header("CONSULTA DE AUDITORIA")
    
    print("Trilha de auditoria completa:")
    trail = blockchain.get_audit_trail(hash_info['hash_id'])
    
    for i, event in enumerate(trail, 1):
        print(f"\n  Evento {i}:")
        print(f"    Timestamp: {event['timestamp']}")
        print(f"    Ação: {event['action']}")
        print(f"    Bloco: {event['block_index']}")
        if 'destinatario' in event['data']:
            print(f"    Destinatário: {event['data']['destinatario']}")
    
    # Verifica integridade
    print_header("VERIFICAÇÃO DE INTEGRIDADE")
    
    print("Verificando integridade da blockchain...")
    is_valid = blockchain.verify_integrity()
    
    if is_valid:
        print("  [OK] BLOCKCHAIN ÍNTEGRA")
        print("  [OK] Todos os blocos estão válidos")
        print("  [OK] A cadeia está intacta")
    else:
        print("  [ERRO] BLOCKCHAIN COMPROMETIDA")
    
    # Estatísticas
    print_header("ESTATÍSTICAS")
    
    stats = blockchain.get_statistics()
    print(f"Total de blocos: {stats['total_blocks']}")
    print(f"Total de edições: {stats['total_edicoes']}")
    print(f"Total de fascículos: {stats['total_fasciculos']}")
    print(f"Total de emails enviados: {stats['total_emails_sent']}")
    
    print("\nBlocos por tipo:")
    for block_type, count in stats['blocks_by_type'].items():
        print(f"  {block_type}: {count}")
    
    # Resumo final
    print_header("DEMONSTRAÇÃO CONCLUÍDA")
    
    print("[OK] Sistema funcionando corretamente!")
    print(f"\nHash ID gerado: {hash_info['hash_id']}")
    print(f"Total de blocos na blockchain: {len(blockchain.chain)}")
    print(f"Blockchain íntegra: {'Sim' if is_valid else 'Não'}")
    
    print("\n" + "-" * 70)
    print("Para usar o sistema em produção:")
    print("  1. Configure o arquivo .env com suas credenciais de email")
    print("  2. Use main.py para gerar hashes de fascículos reais")
    print("  3. Use send_system.py para enviar por email")
    print("  4. Use audit_query.py para consultar a auditoria")
    print("-" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO] Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()
