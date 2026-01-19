"""
Sistema Principal - Geração de Hash para Fascículos
Este script gera hashes criptografados para fascículos e registra na blockchain e MySQL
"""
import sys
import argparse
from pathlib import Path
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from hash_generator import HashGenerator
from crypto_manager import CryptoManager
from blockchain_audit import BlockchainAudit, BlockType
from database import DatabaseManager
from logger import get_logger
from validator import Validator, validar_ou_erro
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH

# Configurar logger
logger = get_logger(__name__)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Gera hash criptografado para um fascículo e registra na blockchain e MySQL'
    )
    parser.add_argument('--edicao', required=True, help='Nome ou número da edição')
    parser.add_argument('--fasciculo', required=True, help='Nome ou número do fascículo')
    parser.add_argument('--pdf', required=True, help='Caminho para o arquivo PDF do fascículo')
    parser.add_argument('--metadata', help='Metadados adicionais em formato JSON', default='{}')
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("SISTEMA DE GERAÇÃO DE HASH PARA FASCÍCULOS")
    logger.info("=" * 70)
    
    try:
        # ===== VALIDAÇÕES =====
        logger.info("Validando entradas...")
        
        # Validar nome da edição
        try:
            validar_ou_erro(Validator.validar_nome, args.edicao, "Edição")
        except ValueError as e:
            logger.error(f"Validação falhou: {e}")
            print(f"\n[ERRO] Erro: {e}")
            return 1
        
        # Validar nome do fascículo
        try:
            validar_ou_erro(Validator.validar_nome, args.fasciculo, "Fascículo")
        except ValueError as e:
            logger.error(f"Validação falhou: {e}")
            print(f"\n[ERRO] Erro: {e}")
            return 1
        
        # Validar PDF
        pdf_path = Path(args.pdf)
        valido, erro = Validator.validar_pdf(str(pdf_path))
        if not valido:
            logger.error(f"Validação de PDF falhou: {erro}")
            print(f"\n[ERRO] Erro: {erro}")
            return 1
        
        # Parse metadata
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            logger.error(f"Metadados inválidos: {e}")
            print(f"\n[ERRO] Erro: Metadados inválidos. Use formato JSON válido")
            return 1
        
        logger.info("[OK] Validações concluídas")
        
        # ===== EXIBIR INFORMAÇÕES =====
        print(f"\nEdição: {args.edicao}")
        print(f"Fascículo: {args.fasciculo}")
        print(f"PDF: {pdf_path}")
        print(f"Tamanho: {pdf_path.stat().st_size / 1024:.2f} KB")
        
        logger.info(f"Edição: {args.edicao}, Fascículo: {args.fasciculo}, PDF: {pdf_path}")
        
        # ===== INICIALIZAR COMPONENTES =====
        print("\n[1/6] Inicializando componentes...")
        logger.info("Inicializando componentes...")
        
        try:
            hash_gen = HashGenerator()
            crypto = CryptoManager(ENCRYPTION_KEY_PATH)
            blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
            db = DatabaseManager()
            
            logger.info("[OK] Componentes inicializados")
        except Exception as e:
            logger.exception("Erro ao inicializar componentes")
            print(f"\n[ERRO] Erro ao inicializar componentes: {e}")
            return 1
        
        # ===== GERAR HASH =====
        print("[2/6] Gerando hash do fascículo...")
        logger.info("Gerando hash do fascículo...")
        
        try:
            hash_info = hash_gen.generate_fasciculo_hash(
                pdf_path=pdf_path,
                edicao=args.edicao,
                fasciculo=args.fasciculo,
                metadata=metadata
            )
            
            print(f"  [OK] Hash ID: {hash_info['hash_id']}")
            print(f"  [OK] Hash do Fascículo: {hash_info['fasciculo_hash'][:32]}...")
            
            logger.info(f"Hash gerado - ID: {hash_info['hash_id']}, Hash: {hash_info['fasciculo_hash'][:16]}...")
        except Exception as e:
            logger.exception("Erro ao gerar hash")
            print(f"\n[ERRO] Erro ao gerar hash: {e}")
            return 1
        
        # ===== REGISTRAR NA BLOCKCHAIN =====
        print("[3/6] Registrando geração na blockchain...")
        logger.info("Registrando na blockchain...")
        
        try:
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
            print(f"  [OK] Bloco adicionado à blockchain")
            logger.info("[OK] Bloco adicionado à blockchain")
        except Exception as e:
            logger.exception("Erro ao adicionar bloco na blockchain")
            print(f"\n[ERRO] Erro ao registrar na blockchain: {e}")
            return 1
        
        # ===== SALVAR NO MYSQL =====
        print("[4/6] Salvando no banco de dados MySQL...")
        logger.info("Salvando no MySQL...")
        
        try:
            if db.connect():
                # Inserir fascículo
                db.inserir_fasciculo(hash_info)
                
                # Inserir log de geração
                db.inserir_log_evento(
                    hash_id=hash_info['hash_id'],
                    evento_tipo='HASH_GENERATED',
                    dados_adicionais={
                        'edicao': args.edicao,
                        'fasciculo': args.fasciculo,
                        'pdf_size': hash_info['pdf_size']
                    }
                )
                
                db.disconnect()
                print(f"  [OK] Dados salvos no MySQL")
                logger.info("[OK] Dados salvos no MySQL")
            else:
                logger.warning("Não foi possível conectar ao MySQL - continuando sem banco")
                print(f"  [AVISO] Aviso: Não foi possível salvar no MySQL (continuando)")
        except Exception as e:
            logger.exception("Erro ao salvar no MySQL")
            print(f"  [AVISO] Aviso: Erro ao salvar no MySQL: {e} (continuando)")
        
        # ===== CRIPTOGRAFAR =====
        print("[5/6] Criptografando informações sensíveis...")
        logger.info("Criptografando informações...")
        
        try:
            encrypted_info = crypto.encrypt_hash(hash_info)
            print(f"  [OK] Dados criptografados")
            logger.info("[OK] Dados criptografados")
        except Exception as e:
            logger.exception("Erro ao criptografar")
            print(f"\n[ERRO] Erro ao criptografar: {e}")
            return 1
        
        # Registrar criptografia na blockchain
        try:
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
            logger.info("[OK] Criptografia registrada na blockchain")
        except Exception as e:
            logger.exception("Erro ao registrar criptografia na blockchain")
            print(f"\n[ERRO] Erro ao registrar criptografia: {e}")
            return 1
        
        # Registrar criptografia no MySQL
        try:
            if db.connect():
                db.inserir_log_evento(
                    hash_id=hash_info['hash_id'],
                    evento_tipo='HASH_ENCRYPTED',
                    dados_adicionais={
                        'encrypted_data_length': len(encrypted_info['encrypted_data'])
                    }
                )
                db.disconnect()
                logger.info("[OK] Criptografia registrada no MySQL")
        except Exception as e:
            logger.warning(f"Erro ao registrar criptografia no MySQL: {e}")
        
        # ===== SALVAR ARQUIVO =====
        print("[6/6] Salvando arquivo de hash...")
        logger.info("Salvando arquivo de hash...")
        
        try:
            output_file = Path('data') / f"hash_{hash_info['hash_id']}.json"
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(encrypted_info, f, indent=2, ensure_ascii=False)
            
            print(f"  [OK] Arquivo salvo: {output_file}")
            logger.info(f"[OK] Arquivo salvo: {output_file}")
        except Exception as e:
            logger.exception("Erro ao salvar arquivo")
            print(f"\n[ERRO] Erro ao salvar arquivo: {e}")
            return 1
        
        # ===== SUCESSO =====
        print("\n" + "=" * 70)
        print("[OK] HASH GERADO E REGISTRADO COM SUCESSO!")
        print("=" * 70)
        print(f"\nHash ID: {hash_info['hash_id']}")
        print(f"Arquivo de hash: {output_file}")
        print(f"\nPara enviar este fascículo, use:")
        print(f"  python send_system.py --hash-id {hash_info['hash_id']} --destinatario email@exemplo.com")
        print(f"\nPara consultar a auditoria, use:")
        print(f"  python audit_query.py --hash-id {hash_info['hash_id']}")
        print(f"  python consultar_db.py --hash-id {hash_info['hash_id']}")
        
        logger.info("=" * 70)
        logger.info("HASH GERADO E REGISTRADO COM SUCESSO!")
        logger.info(f"Hash ID: {hash_info['hash_id']}")
        logger.info("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Operação cancelada pelo usuário")
        print("\n\n[AVISO] Operação cancelada pelo usuário")
        return 130
    
    except Exception as e:
        logger.exception("Erro inesperado")
        print(f"\n[ERRO] Erro inesperado: {e}")
        print(f"Verifique o arquivo de log para mais detalhes: logs/auditoria_*.log")
        return 1


if __name__ == "__main__":
    sys.exit(main())
