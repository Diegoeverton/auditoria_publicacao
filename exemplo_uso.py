"""
Exemplo de Uso Completo do Sistema
Este arquivo demonstra como usar o sistema programaticamente
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from hash_generator import HashGenerator
from crypto_manager import CryptoManager
from blockchain_audit import BlockchainAudit, BlockType
from email_sender import EmailSender
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH, SMTP_CONFIG


def exemplo_completo():
    """Exemplo de uso completo do sistema"""
    
    # 1. INICIALIZAÇÃO
    print("=" * 70)
    print("EXEMPLO DE USO COMPLETO DO SISTEMA")
    print("=" * 70)
    
    # Inicializa componentes
    hash_gen = HashGenerator()
    crypto = CryptoManager(ENCRYPTION_KEY_PATH)
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    email_sender = EmailSender(SMTP_CONFIG)
    
    print("\n✓ Componentes inicializados")
    
    # 2. GERAÇÃO DE HASH
    print("\n[PASSO 1] Gerando hash para fascículo...")
    
    # Caminho para o PDF (ajuste conforme necessário)
    pdf_path = Path('fasciculos/demo_fasciculo.pdf')
    
    # Se o PDF não existir, cria um de exemplo
    if not pdf_path.exists():
        pdf_path.parent.mkdir(exist_ok=True)
        pdf_path.write_bytes(b'%PDF-1.4\n%Demo PDF\n')
        print(f"  ✓ PDF de exemplo criado: {pdf_path}")
    
    # Gera hash
    hash_info = hash_gen.generate_fasciculo_hash(
        pdf_path=pdf_path,
        edicao="Exemplo 001",
        fasciculo="Fascículo 01",
        metadata={
            'autor': 'Sistema de Auditoria',
            'versao': '1.0',
            'tipo': 'exemplo'
        }
    )
    
    print(f"  ✓ Hash ID: {hash_info['hash_id']}")
    print(f"  ✓ Hash: {hash_info['fasciculo_hash'][:32]}...")
    
    # Registra na blockchain
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': hash_info['edicao'],
            'fasciculo': hash_info['fasciculo'],
            'fasciculo_hash': hash_info['fasciculo_hash'],
            'action': 'Hash gerado'
        },
        block_type=BlockType.HASH_GENERATED
    )
    print("  ✓ Registrado na blockchain")
    
    # 3. CRIPTOGRAFIA
    print("\n[PASSO 2] Criptografando informações...")
    
    encrypted_info = crypto.encrypt_hash(hash_info)
    print(f"  ✓ Dados criptografados")
    
    # Registra criptografia
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': hash_info['edicao'],
            'fasciculo': hash_info['fasciculo'],
            'action': 'Hash criptografado'
        },
        block_type=BlockType.HASH_ENCRYPTED
    )
    print("  ✓ Criptografia registrada na blockchain")
    
    # 4. DESCRIPTOGRAFIA (quando for enviar)
    print("\n[PASSO 3] Descriptografando para envio...")
    
    decrypted_info = crypto.decrypt_hash(encrypted_info)
    print(f"  ✓ Dados descriptografados")
    
    # Registra descriptografia
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': hash_info['edicao'],
            'fasciculo': hash_info['fasciculo'],
            'destinatario': 'exemplo@email.com',
            'action': 'Hash descriptografado para envio'
        },
        block_type=BlockType.HASH_DECRYPTED
    )
    print("  ✓ Descriptografia registrada na blockchain")
    
    # 5. ENVIO (simulado - requer configuração de email)
    print("\n[PASSO 4] Preparando envio...")
    
    # Verifica se email está configurado
    if SMTP_CONFIG['user'] and SMTP_CONFIG['password']:
        print("  ⚠ Email configurado - envio real seria executado")
        print("  ℹ Para segurança, não enviando email neste exemplo")
        # Descomente para enviar de verdade:
        # result = email_sender.send_fasciculo(
        #     destinatario='exemplo@email.com',
        #     fasciculo_info=decrypted_info,
        #     pdf_path=pdf_path
        # )
    else:
        print("  ℹ Email não configurado - simulando envio")
    
    # Registra envio (simulado)
    blockchain.add_block(
        data={
            'hash_id': hash_info['hash_id'],
            'edicao': hash_info['edicao'],
            'fasciculo': hash_info['fasciculo'],
            'destinatario': 'exemplo@email.com',
            'fasciculo_hash': decrypted_info['fasciculo_hash'],
            'action': 'Fascículo enviado (EXEMPLO)'
        },
        block_type=BlockType.EMAIL_SENT
    )
    print("  ✓ Envio registrado na blockchain")
    
    # 6. CONSULTA DE AUDITORIA
    print("\n[PASSO 5] Consultando trilha de auditoria...")
    
    trail = blockchain.get_audit_trail(hash_info['hash_id'])
    print(f"  ✓ Total de eventos: {len(trail)}")
    
    for i, event in enumerate(trail, 1):
        print(f"\n  Evento {i}:")
        print(f"    Ação: {event['action']}")
        print(f"    Timestamp: {event['timestamp']}")
        print(f"    Bloco: {event['block_index']}")
    
    # 7. VERIFICAÇÃO DE INTEGRIDADE
    print("\n[PASSO 6] Verificando integridade da blockchain...")
    
    is_valid = blockchain.verify_integrity()
    if is_valid:
        print("  ✓ Blockchain íntegra - todos os blocos válidos")
    else:
        print("  ✗ Blockchain comprometida!")
    
    # 8. ESTATÍSTICAS
    print("\n[PASSO 7] Estatísticas do sistema...")
    
    stats = blockchain.get_statistics()
    print(f"  Total de blocos: {stats['total_blocks']}")
    print(f"  Total de edições: {stats['total_edicoes']}")
    print(f"  Total de fascículos: {stats['total_fasciculos']}")
    print(f"  Total de emails enviados: {stats['total_emails_sent']}")
    
    # RESUMO
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"\n✓ Hash ID: {hash_info['hash_id']}")
    print(f"✓ Edição: {hash_info['edicao']}")
    print(f"✓ Fascículo: {hash_info['fasciculo']}")
    print(f"✓ Total de eventos registrados: {len(trail)}")
    print(f"✓ Blockchain íntegra: {'Sim' if is_valid else 'Não'}")
    
    return hash_info['hash_id']


def exemplo_consulta_por_edicao():
    """Exemplo de consulta por edição"""
    
    print("\n" + "=" * 70)
    print("EXEMPLO: CONSULTA POR EDIÇÃO")
    print("=" * 70)
    
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    
    # Consulta todos os fascículos de uma edição
    edicao = "Exemplo 001"
    blocks = blockchain.get_blocks_by_edicao(edicao)
    
    print(f"\nFascículos da edição '{edicao}':")
    print(f"Total de blocos relacionados: {len(blocks)}")
    
    # Agrupa por hash_id
    fasciculos = {}
    for block in blocks:
        hash_id = block.data.get('hash_id')
        if hash_id and hash_id not in fasciculos:
            fasciculos[hash_id] = {
                'fasciculo': block.data.get('fasciculo', 'N/A'),
                'eventos': []
            }
        if hash_id:
            fasciculos[hash_id]['eventos'].append(block.block_type)
    
    for hash_id, info in fasciculos.items():
        print(f"\n  Fascículo: {info['fasciculo']}")
        print(f"  Hash ID: {hash_id}")
        print(f"  Eventos: {len(info['eventos'])}")
        print(f"  Status: {'✓ Enviado' if BlockType.EMAIL_SENT.value in info['eventos'] else '⏳ Pendente'}")


def exemplo_verificacao_hash():
    """Exemplo de verificação de hash de um PDF"""
    
    print("\n" + "=" * 70)
    print("EXEMPLO: VERIFICAÇÃO DE HASH")
    print("=" * 70)
    
    hash_gen = HashGenerator()
    
    # Verifica se um PDF corresponde ao hash original
    pdf_path = Path('fasciculos/demo_fasciculo.pdf')
    
    if not pdf_path.exists():
        print("\n⚠ PDF de exemplo não encontrado")
        return
    
    # Gera hash atual
    current_hash_info = hash_gen.generate_fasciculo_hash(
        pdf_path=pdf_path,
        edicao="Teste",
        fasciculo="Teste",
        metadata={}
    )
    
    print(f"\nHash atual do PDF: {current_hash_info['fasciculo_hash'][:32]}...")
    print("✓ Hash gerado com sucesso")
    print("\nEste hash pode ser comparado com o hash original para verificar integridade")


if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  EXEMPLOS DE USO DO SISTEMA DE AUDITORIA DE PUBLICAÇÃO".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    try:
        # Executa exemplo completo
        hash_id = exemplo_completo()
        
        # Executa exemplo de consulta por edição
        exemplo_consulta_por_edicao()
        
        # Executa exemplo de verificação de hash
        exemplo_verificacao_hash()
        
        print("\n" + "=" * 70)
        print("TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("=" * 70)
        print("\nPróximos passos:")
        print("  1. Configure o arquivo .env com suas credenciais de email")
        print("  2. Use main.py para gerar hashes de fascículos reais")
        print("  3. Use send_system.py para enviar por email")
        print("  4. Use audit_query.py para consultar a auditoria")
        print("\nDocumentação completa: README.md e QUICKSTART.md")
        
    except Exception as e:
        print(f"\n✗ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
