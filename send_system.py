"""
Sistema de Envio - Descriptografa e Envia Fascículos
Este script descriptografa hashes e envia fascículos por email com logging e validações
"""
import sys
import argparse
from pathlib import Path
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import smtplib

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crypto_manager import CryptoManager
from email_sender import EmailSender
from blockchain_audit import BlockchainAudit, BlockType
from database import DatabaseManager
from logger import get_logger
from validator import Validator, validar_ou_erro
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH, SMTP_CONFIG

# Configurar logger
logger = get_logger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((smtplib.SMTPException, ConnectionError)),
    reraise=True
)
def enviar_email_com_retry(email_sender, destinatario, fasciculo_info, pdf_path, assunto, mensagem):
    """
    Envia email com retry automático em caso de falha
    
    Args:
        email_sender: Instância do EmailSender
        destinatario: Email do destinatário
        fasciculo_info: Informações do fascículo
        pdf_path: Caminho do PDF
        assunto: Assunto do email
        mensagem: Mensagem adicional
    
    Returns:
        Resultado do envio
    """
    logger.info(f"Tentando enviar email para {destinatario}...")
    return email_sender.send_fasciculo(
        destinatario=destinatario,
        fasciculo_info=fasciculo_info,
        pdf_path=pdf_path,
        assunto=assunto,
        mensagem_adicional=mensagem
    )


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Descriptografa hash e envia fascículo por email com retry automático'
    )
    parser.add_argument('--hash-id', required=True, help='ID do hash do fascículo')
    parser.add_argument('--destinatario', required=True, help='Email do destinatário')
    parser.add_argument('--assunto', help='Assunto do email (opcional)')
    parser.add_argument('--mensagem', help='Mensagem adicional no email (opcional)')
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("SISTEMA DE ENVIO DE FASCÍCULOS")
    logger.info("=" * 70)
    
    try:
        # ===== VALIDAÇÕES =====
        logger.info("Validando entradas...")
        
        # Validar hash ID
        try:
            validar_ou_erro(Validator.validar_hash_id, args.hash_id)
        except ValueError as e:
            logger.error(f"Validação falhou: {e}")
            print(f"\n✗ Erro: {e}")
            return 1
        
        # Validar email do destinatário
        try:
            validar_ou_erro(Validator.validar_email, args.destinatario)
        except ValueError as e:
            logger.error(f"Validação falhou: {e}")
            print(f"\n✗ Erro: {e}")
            return 1
        
        logger.info("✓ Validações concluídas")
        
        # ===== EXIBIR INFORMAÇÕES =====
        print("=" * 70)
        print("SISTEMA DE ENVIO DE FASCÍCULOS")
        print("=" * 70)
        print(f"\nHash ID: {args.hash_id}")
        print(f"Destinatário: {args.destinatario}")
        
        logger.info(f"Hash ID: {args.hash_id}, Destinatário: {args.destinatario}")
        
        # ===== CARREGAR ARQUIVO DE HASH =====
        hash_file = Path('data') / f"hash_{args.hash_id}.json"
        
        if not hash_file.exists():
            logger.error(f"Arquivo de hash não encontrado: {hash_file}")
            print(f"\n✗ Erro: Arquivo de hash não encontrado: {hash_file}")
            print(f"  Certifique-se de que o hash foi gerado usando main.py")
            return 1
        
        # ===== INICIALIZAR COMPONENTES =====
        print("\n[1/7] Inicializando componentes...")
        logger.info("Inicializando componentes...")
        
        try:
            crypto = CryptoManager(ENCRYPTION_KEY_PATH)
            blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
            email_sender = EmailSender(SMTP_CONFIG)
            db = DatabaseManager()
            
            logger.info("✓ Componentes inicializados")
        except Exception as e:
            logger.exception("Erro ao inicializar componentes")
            print(f"\n✗ Erro ao inicializar componentes: {e}")
            return 1
        
        # ===== CARREGAR HASH CRIPTOGRAFADO =====
        print("[2/7] Carregando hash criptografado...")
        logger.info("Carregando hash criptografado...")
        
        try:
            with open(hash_file, 'r', encoding='utf-8') as f:
                encrypted_info = json.load(f)
            
            print(f"  ✓ Edição: {encrypted_info['edicao']}")
            print(f"  ✓ Fascículo: {encrypted_info['fasciculo']}")
            
            logger.info(f"Hash carregado - Edição: {encrypted_info['edicao']}, Fascículo: {encrypted_info['fasciculo']}")
        except Exception as e:
            logger.exception("Erro ao carregar hash")
            print(f"\n✗ Erro ao carregar hash: {e}")
            return 1
        
        # ===== DESCRIPTOGRAFAR =====
        print("[3/7] Descriptografando informações...")
        logger.info("Descriptografando informações...")
        
        try:
            decrypted_info = crypto.decrypt_hash(encrypted_info)
            print(f"  ✓ Hash descriptografado: {decrypted_info['fasciculo_hash'][:32]}...")
            
            logger.info(f"Hash descriptografado: {decrypted_info['fasciculo_hash'][:16]}...")
        except Exception as e:
            logger.exception("Erro ao descriptografar")
            print(f"\n✗ Erro ao descriptografar: {e}")
            return 1
        
        # ===== REGISTRAR DESCRIPTOGRAFIA =====
        print("[4/7] Registrando descriptografia...")
        logger.info("Registrando descriptografia...")
        
        # Blockchain
        try:
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
            print(f"  ✓ Registrado na blockchain")
            logger.info("✓ Descriptografia registrada na blockchain")
        except Exception as e:
            logger.exception("Erro ao registrar descriptografia na blockchain")
            print(f"\n✗ Erro ao registrar na blockchain: {e}")
            return 1
        
        # MySQL
        try:
            if db.connect():
                db.inserir_log_evento(
                    hash_id=args.hash_id,
                    evento_tipo='HASH_DECRYPTED',
                    destinatario=args.destinatario,
                    dados_adicionais={
                        'edicao': encrypted_info['edicao'],
                        'fasciculo': encrypted_info['fasciculo']
                    }
                )
                db.disconnect()
                print(f"  ✓ Registrado no MySQL")
                logger.info("✓ Descriptografia registrada no MySQL")
        except Exception as e:
            logger.warning(f"Erro ao registrar descriptografia no MySQL: {e}")
            print(f"  ⚠ Aviso: Erro ao registrar no MySQL (continuando)")
        
        # ===== VERIFICAR PDF =====
        pdf_path = Path(decrypted_info['pdf_path'])
        if not pdf_path.exists():
            logger.warning(f"PDF não encontrado: {pdf_path}")
            print(f"\n⚠ Aviso: PDF não encontrado em {pdf_path}")
            print(f"  O email será enviado sem anexo")
            pdf_path = None
        else:
            # Validar PDF
            valido, erro = Validator.validar_pdf(str(pdf_path))
            if not valido:
                logger.error(f"PDF inválido: {erro}")
                print(f"\n✗ Erro: {erro}")
                return 1
        
        # ===== VERIFICAR CONFIGURAÇÃO DE EMAIL =====
        if not SMTP_CONFIG['user'] or not SMTP_CONFIG['password']:
            logger.error("Configurações de email não definidas")
            print("\n✗ Erro: Configurações de email não definidas")
            print("  Configure as credenciais SMTP no arquivo .env")
            print("\nVeja o guia: CONFIGURAR_GMAIL.md")
            return 1
        
        # ===== ENVIAR EMAIL =====
        print("[5/7] Enviando fascículo por email...")
        logger.info(f"Enviando email para {args.destinatario}...")
        
        try:
            send_result = enviar_email_com_retry(
                email_sender=email_sender,
                destinatario=args.destinatario,
                fasciculo_info=decrypted_info,
                pdf_path=pdf_path,
                assunto=args.assunto,
                mensagem=args.mensagem
            )
            
            if send_result['success']:
                print(f"  ✓ Email enviado com sucesso!")
                logger.info(f"✓ Email enviado para {args.destinatario}")
            else:
                logger.error(f"Erro ao enviar email: {send_result.get('error')}")
                print(f"  ✗ Erro ao enviar email: {send_result.get('error')}")
                return 1
        
        except Exception as e:
            logger.exception("Erro ao enviar email após 3 tentativas")
            print(f"\n✗ Erro ao enviar email após 3 tentativas: {e}")
            print(f"  Verifique:")
            print(f"  1. Configurações de email no .env")
            print(f"  2. Conexão com internet")
            print(f"  3. Limites de envio do provedor")
            return 1
        
        # ===== REGISTRAR ENVIO =====
        print("[6/7] Registrando envio...")
        logger.info("Registrando envio...")
        
        # Blockchain
        try:
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
            print(f"  ✓ Registrado na blockchain")
            logger.info("✓ Envio registrado na blockchain")
        except Exception as e:
            logger.exception("Erro ao registrar envio na blockchain")
            print(f"\n✗ Erro ao registrar na blockchain: {e}")
            return 1
        
        # MySQL
        print("[7/7] Salvando no banco de dados...")
        try:
            if db.connect():
                db.inserir_log_evento(
                    hash_id=args.hash_id,
                    evento_tipo='EMAIL_SENT',
                    destinatario=args.destinatario,
                    dados_adicionais={
                        'edicao': encrypted_info['edicao'],
                        'fasciculo': encrypted_info['fasciculo'],
                        'timestamp_envio': send_result['timestamp']
                    }
                )
                db.disconnect()
                print(f"  ✓ Registrado no MySQL")
                logger.info("✓ Envio registrado no MySQL")
        except Exception as e:
            logger.warning(f"Erro ao registrar envio no MySQL: {e}")
            print(f"  ⚠ Aviso: Erro ao registrar no MySQL (continuando)")
        
        # ===== SUCESSO =====
        print("\n" + "=" * 70)
        print("✓ FASCÍCULO ENVIADO E REGISTRADO COM SUCESSO!")
        print("=" * 70)
        print(f"\nDestinatário: {args.destinatario}")
        print(f"Hash do Fascículo: {decrypted_info['fasciculo_hash']}")
        print(f"\nTrilha de auditoria completa disponível:")
        print(f"  python audit_query.py --hash-id {args.hash_id}")
        print(f"  python consultar_db.py --hash-id {args.hash_id}")
        
        logger.info("=" * 70)
        logger.info("FASCÍCULO ENVIADO E REGISTRADO COM SUCESSO!")
        logger.info(f"Destinatário: {args.destinatario}")
        logger.info("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Operação cancelada pelo usuário")
        print("\n\n⚠ Operação cancelada pelo usuário")
        return 130
    
    except Exception as e:
        logger.exception("Erro inesperado")
        print(f"\n✗ Erro inesperado: {e}")
        print(f"Verifique o arquivo de log para mais detalhes: logs/auditoria_*.log")
        return 1


if __name__ == "__main__":
    sys.exit(main())
