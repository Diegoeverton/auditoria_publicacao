"""
Sistema de Envio - Descriptografa e Envia Fascículos
Este script descriptografa hashes e envia fascículos por email
"""
import sys
import argparse
from pathlib import Path
import json

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crypto_manager import CryptoManager
from email_sender import EmailSender
from blockchain_audit import BlockchainAudit, BlockType
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH, SMTP_CONFIG


def main():
    parser = argparse.ArgumentParser(
        description='Descriptografa hash e envia fascículo por email'
    )
    parser.add_argument('--hash-id', required=True, help='ID do hash do fascículo')
    parser.add_argument('--destinatario', required=True, help='Email do destinatário')
    parser.add_argument('--assunto', help='Assunto do email (opcional)')
    parser.add_argument('--mensagem', help='Mensagem adicional no email (opcional)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("SISTEMA DE ENVIO DE FASCÍCULOS")
    print("=" * 70)
    print(f"\nHash ID: {args.hash_id}")
    print(f"Destinatário: {args.destinatario}")
    
    # Carrega arquivo de hash
    hash_file = Path('data') / f"hash_{args.hash_id}.json"
    
    if not hash_file.exists():
        print(f"\n✗ Erro: Arquivo de hash não encontrado: {hash_file}")
        print(f"  Certifique-se de que o hash foi gerado usando main.py")
        return 1
    
    # Inicializa componentes
    print("\n[1/6] Inicializando componentes...")
    crypto = CryptoManager(ENCRYPTION_KEY_PATH)
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    email_sender = EmailSender(SMTP_CONFIG)
    
    # Carrega hash criptografado
    print("[2/6] Carregando hash criptografado...")
    with open(hash_file, 'r', encoding='utf-8') as f:
        encrypted_info = json.load(f)
    
    print(f"  ✓ Edição: {encrypted_info['edicao']}")
    print(f"  ✓ Fascículo: {encrypted_info['fasciculo']}")
    
    # Descriptografa informações
    print("[3/6] Descriptografando informações...")
    decrypted_info = crypto.decrypt_hash(encrypted_info)
    print(f"  ✓ Hash descriptografado: {decrypted_info['fasciculo_hash'][:32]}...")
    
    # Registra descriptografia na blockchain
    print("[4/6] Registrando descriptografia na blockchain...")
    blockchain.add_block(
        data={
            'hash_id': args.hash_id,
            'edicao': encrypted_info['edicao'],
            'fasciculo': encrypted_info['fasciculo'],
            'destinatario': args.destinatario,
            'action': 'Hash descriptografado para envio'
        },
        block_type=BlockType.HASH_DECRYPTED
    )
    print(f"  ✓ Bloco de descriptografia adicionado")
    
    # Verifica PDF
    pdf_path = Path(decrypted_info['pdf_path'])
    if not pdf_path.exists():
        print(f"\n⚠ Aviso: PDF não encontrado em {pdf_path}")
        print(f"  O email será enviado sem anexo")
        pdf_path = None
    
    # Verifica configuração de email
    if not SMTP_CONFIG['user'] or not SMTP_CONFIG['password']:
        print("\n✗ Erro: Configurações de email não definidas")
        print("  Configure as credenciais SMTP no arquivo .env")
        print("\nExemplo:")
        print("  SMTP_USER=seu_email@gmail.com")
        print("  SMTP_PASSWORD=sua_senha_ou_app_password")
        return 1
    
    # Envia email
    print("[5/6] Enviando fascículo por email...")
    send_result = email_sender.send_fasciculo(
        destinatario=args.destinatario,
        fasciculo_info=decrypted_info,
        pdf_path=pdf_path,
        assunto=args.assunto,
        mensagem_adicional=args.mensagem
    )
    
    if send_result['success']:
        print(f"  ✓ Email enviado com sucesso!")
    else:
        print(f"  ✗ Erro ao enviar email: {send_result.get('error')}")
        return 1
    
    # Registra envio na blockchain
    print("[6/6] Registrando envio na blockchain...")
    blockchain.add_block(
        data={
            'hash_id': args.hash_id,
            'edicao': encrypted_info['edicao'],
            'fasciculo': encrypted_info['fasciculo'],
            'destinatario': args.destinatario,
            'fasciculo_hash': decrypted_info['fasciculo_hash'],
            'timestamp_envio': send_result['timestamp'],
            'action': 'Fascículo enviado por email'
        },
        block_type=BlockType.EMAIL_SENT
    )
    print(f"  ✓ Bloco de envio adicionado")
    
    print("\n" + "=" * 70)
    print("✓ FASCÍCULO ENVIADO E REGISTRADO COM SUCESSO!")
    print("=" * 70)
    print(f"\nDestinatário: {args.destinatario}")
    print(f"Hash do Fascículo: {decrypted_info['fasciculo_hash']}")
    print(f"\nTrilha de auditoria completa disponível:")
    print(f"  python audit_query.py --hash-id {args.hash_id}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
