"""
Script de Envio em Massa
Envia o mesmo fascículo para múltiplos destinatários com logging, validações e MySQL
"""
import sys
import time
from pathlib import Path
import json
from datetime import datetime
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


def carregar_destinatarios(arquivo_destinatarios):
    """Carrega lista de destinatários de um arquivo"""
    arquivo = Path(arquivo_destinatarios)
    
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    
    destinatarios = []
    
    # Arquivo TXT
    if arquivo.suffix == '.txt':
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                email = linha.strip()
                if email:
                    # Validar email
                    valido, erro = Validator.validar_email(email)
                    if valido:
                        destinatarios.append({'email': email, 'nome': ''})
                    else:
                        logger.warning(f"Email inválido ignorado: {email} - {erro}")
    
    # Arquivo JSON
    elif arquivo.suffix == '.json':
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                for email in data:
                    valido, erro = Validator.validar_email(email)
                    if valido:
                        destinatarios.append({'email': email, 'nome': ''})
                    else:
                        logger.warning(f"Email inválido ignorado: {email} - {erro}")
            
            elif isinstance(data, list) and all(isinstance(x, dict) for x in data):
                for item in data:
                    email = item.get('email', '')
                    valido, erro = Validator.validar_email(email)
                    if valido:
                        destinatarios.append(item)
                    else:
                        logger.warning(f"Email inválido ignorado: {email} - {erro}")
    
    # Arquivo CSV
    elif arquivo.suffix == '.csv':
        import csv
        with open(arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Pula cabeçalho
            for row in reader:
                if row:
                    email = row[0].strip()
                    valido, erro = Validator.validar_email(email)
                    if valido:
                        destinatarios.append({
                            'email': email,
                            'nome': row[1].strip() if len(row) > 1 else ''
                        })
                    else:
                        logger.warning(f"Email inválido ignorado: {email} - {erro}")
    
    else:
        raise ValueError(f"Formato de arquivo não suportado: {arquivo.suffix}")
    
    return destinatarios


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((smtplib.SMTPException, ConnectionError)),
    reraise=True
)
def enviar_email_com_retry(email_sender, destinatario, fasciculo_info, pdf_path, mensagem):
    """Envia email com retry automático"""
    return email_sender.send_fasciculo(
        destinatario=destinatario,
        fasciculo_info=fasciculo_info,
        pdf_path=pdf_path,
        mensagem_adicional=mensagem
    )


def enviar_em_massa(hash_id, arquivo_destinatarios, intervalo=1, lote_tamanho=100):
    """Envia o mesmo fascículo para múltiplos destinatários"""
    
    logger.info("=" * 70)
    logger.info("ENVIO EM MASSA DE FASCÍCULO")
    logger.info(f"Hash ID: {hash_id}, Arquivo: {arquivo_destinatarios}")
    logger.info("=" * 70)
    
    print("=" * 70)
    print("ENVIO EM MASSA DE FASCÍCULO")
    print("=" * 70)
    print(f"\nHash ID: {hash_id}")
    print(f"Arquivo de destinatários: {arquivo_destinatarios}")
    print(f"Intervalo entre envios: {intervalo}s")
    print(f"Tamanho do lote: {lote_tamanho} emails\n")
    
    try:
        # Validar hash ID
        validar_ou_erro(Validator.validar_hash_id, hash_id)
        
        # Validar intervalo e lote
        validar_ou_erro(Validator.validar_intervalo, intervalo)
        validar_ou_erro(Validator.validar_lote, lote_tamanho)
        
        # Carrega destinatários
        print("[1/6] Carregando lista de destinatários...")
        logger.info("Carregando destinatários...")
        
        destinatarios = carregar_destinatarios(arquivo_destinatarios)
        print(f"  ✓ {len(destinatarios)} destinatário(s) válido(s)")
        logger.info(f"✓ {len(destinatarios)} destinatários carregados")
        
        if len(destinatarios) == 0:
            print("  ✗ Nenhum destinatário válido encontrado")
            logger.error("Nenhum destinatário válido")
            return
        
        # Carrega arquivo de hash
        hash_file = Path('data') / f"hash_{hash_id}.json"
        if not hash_file.exists():
            logger.error(f"Arquivo de hash não encontrado: {hash_file}")
            print(f"\n✗ Erro: Arquivo de hash não encontrado: {hash_file}")
            return
        
        # Inicializa componentes
        print("\n[2/6] Inicializando componentes...")
        logger.info("Inicializando componentes...")
        
        crypto = CryptoManager(ENCRYPTION_KEY_PATH)
        blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
        email_sender = EmailSender(SMTP_CONFIG)
        db = DatabaseManager()
        
        print("  ✓ Componentes inicializados")
        logger.info("✓ Componentes inicializados")
        
        # Carrega e descriptografa hash
        print("\n[3/6] Carregando informações do fascículo...")
        logger.info("Carregando fascículo...")
        
        with open(hash_file, 'r', encoding='utf-8') as f:
            encrypted_info = json.load(f)
        
        decrypted_info = crypto.decrypt_hash(encrypted_info)
        
        print(f"  ✓ Edição: {encrypted_info['edicao']}")
        print(f"  ✓ Fascículo: {encrypted_info['fasciculo']}")
        logger.info(f"Fascículo carregado - Edição: {encrypted_info['edicao']}")
        
        # Verifica PDF
        pdf_path = Path(decrypted_info['pdf_path'])
        if not pdf_path.exists():
            logger.warning(f"PDF não encontrado: {pdf_path}")
            print(f"\n⚠ Aviso: PDF não encontrado em {pdf_path}")
            print(f"  O email será enviado sem anexo")
            pdf_path = None
        else:
            valido, erro = Validator.validar_pdf(str(pdf_path))
            if not valido:
                logger.error(f"PDF inválido: {erro}")
                print(f"\n✗ Erro: {erro}")
                return
            pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ PDF encontrado ({pdf_size_mb:.2f} MB)")
        
        # Registra início no MySQL
        print("\n[4/6] Registrando início no banco de dados...")
        logger.info("Registrando início no MySQL...")
        
        envio_massa_id = None
        if db.connect():
            try:
                cursor = db.connection.cursor()
                query = """
                    INSERT INTO envios_massa 
                    (hash_id, total_destinatarios, status)
                    VALUES (%s, %s, 'EM_ANDAMENTO')
                """
                cursor.execute(query, (hash_id, len(destinatarios)))
                envio_massa_id = cursor.lastrowid
                cursor.close()
                print(f"  ✓ Registrado no MySQL (ID: {envio_massa_id})")
                logger.info(f"✓ Envio em massa registrado no MySQL (ID: {envio_massa_id})")
            except Exception as e:
                logger.warning(f"Erro ao registrar no MySQL: {e}")
                print(f"  ⚠ Aviso: Erro ao registrar no MySQL (continuando)")
        
        # Registra início na blockchain
        print("[5/6] Registrando início na blockchain...")
        blockchain.add_block(
            data={
                'hash_id': hash_id,
                'edicao': encrypted_info['edicao'],
                'fasciculo': encrypted_info['fasciculo'],
                'total_destinatarios': len(destinatarios),
                'envio_massa_id': envio_massa_id,
                'action': 'Início de envio em massa'
            },
            block_type=BlockType.HASH_DECRYPTED
        )
        print("  ✓ Registrado na blockchain")
        logger.info("✓ Início registrado na blockchain")
        
        # Envio em massa
        print("\n[6/6] Enviando para destinatários...")
        print("-" * 70)
        logger.info(f"Iniciando envio para {len(destinatarios)} destinatários...")
        
        enviados = 0
        erros = 0
        inicio = time.time()
        
        for i, dest in enumerate(destinatarios, 1):
            email = dest['email']
            nome = dest.get('nome', '')
            
            mensagem = f"Prezado(a) {nome},\n\n" if nome else None
            
            print(f"[{i}/{len(destinatarios)}] Enviando para: {email}", end='')
            if nome:
                print(f" ({nome})", end='')
            print("...", end='', flush=True)
            
            try:
                result = enviar_email_com_retry(
                    email_sender=email_sender,
                    destinatario=email,
                    fasciculo_info=decrypted_info,
                    pdf_path=pdf_path,
                    mensagem=mensagem
                )
                
                if result['success']:
                    print(" ✓")
                    enviados += 1
                    logger.info(f"✓ Email enviado para {email} ({i}/{len(destinatarios)})")
                    
                    # Registra na blockchain
                    blockchain.add_block(
                        data={
                            'hash_id': hash_id,
                            'edicao': encrypted_info['edicao'],
                            'fasciculo': encrypted_info['fasciculo'],
                            'destinatario': email,
                            'nome_destinatario': nome,
                            'numero_envio': i,
                            'total_envios': len(destinatarios),
                            'action': f'Email enviado ({i}/{len(destinatarios)})'
                        },
                        block_type=BlockType.EMAIL_SENT
                    )
                    
                    # Registra no MySQL
                    if db.connection and db.connection.is_connected():
                        db.inserir_log_evento(
                            hash_id=hash_id,
                            evento_tipo='EMAIL_SENT',
                            destinatario=email,
                            nome_destinatario=nome,
                            dados_adicionais={
                                'numero_envio': i,
                                'total_envios': len(destinatarios),
                                'envio_massa_id': envio_massa_id
                            }
                        )
                else:
                    print(f" ✗ Erro: {result.get('error', 'Desconhecido')}")
                    erros += 1
                    logger.error(f"✗ Erro ao enviar para {email}: {result.get('error')}")
            
            except Exception as e:
                print(f" ✗ Exceção: {e}")
                erros += 1
                logger.exception(f"Exceção ao enviar para {email}")
            
            # Intervalo entre envios
            if i < len(destinatarios):
                if i % lote_tamanho == 0:
                    pausa = intervalo * 5
                    print(f"\n⏸ Pausa de {pausa}s após {lote_tamanho} envios...")
                    logger.info(f"Pausa de {pausa}s após lote de {lote_tamanho}")
                    time.sleep(pausa)
                else:
                    time.sleep(intervalo)
        
        # Estatísticas finais
        tempo_total = time.time() - inicio
        
        print("-" * 70)
        print("\n" + "=" * 70)
        print("ENVIO EM MASSA CONCLUÍDO")
        print("=" * 70)
        
        print(f"\n📊 Estatísticas:")
        print(f"  Total de destinatários: {len(destinatarios)}")
        print(f"  ✓ Enviados com sucesso: {enviados}")
        print(f"  ✗ Erros: {erros}")
        print(f"  Taxa de sucesso: {(enviados/len(destinatarios)*100):.1f}%")
        print(f"  Tempo total: {tempo_total/60:.1f} minutos")
        print(f"  Média: {tempo_total/len(destinatarios):.1f}s por email")
        
        logger.info("=" * 70)
        logger.info(f"ENVIO EM MASSA CONCLUÍDO - Enviados: {enviados}, Erros: {erros}")
        logger.info("=" * 70)
        
        # Atualiza MySQL
        if db.connection and db.connection.is_connected() and envio_massa_id:
            try:
                cursor = db.connection.cursor()
                query = """
                    UPDATE envios_massa 
                    SET enviados = %s, erros = %s, tempo_total_minutos = %s, 
                        status = 'CONCLUIDO', completed_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (enviados, erros, tempo_total / 60, envio_massa_id))
                cursor.close()
                logger.info("✓ Estatísticas atualizadas no MySQL")
            except Exception as e:
                logger.warning(f"Erro ao atualizar MySQL: {e}")
        
        if db.connection:
            db.disconnect()
        
        # Registra conclusão na blockchain
        blockchain.add_block(
            data={
                'hash_id': hash_id,
                'edicao': encrypted_info['edicao'],
                'fasciculo': encrypted_info['fasciculo'],
                'total_destinatarios': len(destinatarios),
                'enviados': enviados,
                'erros': erros,
                'tempo_total_minutos': tempo_total / 60,
                'envio_massa_id': envio_massa_id,
                'action': 'Conclusão de envio em massa'
            },
            block_type=BlockType.VERIFICATION
        )
        
        print(f"\n✓ Envio em massa registrado na blockchain e MySQL")
        print(f"\nPara consultar a auditoria:")
        print(f"  python audit_query.py --hash-id {hash_id}")
        print(f"  python consultar_db.py --hash-id {hash_id}")
    
    except Exception as e:
        logger.exception("Erro durante envio em massa")
        print(f"\n✗ Erro: {e}")
        print(f"Verifique o arquivo de log: logs/auditoria_*.log")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Envia o mesmo fascículo para múltiplos destinatários'
    )
    parser.add_argument('--hash-id', required=True, help='ID do hash do fascículo')
    parser.add_argument('--destinatarios', required=True, 
                       help='Arquivo com lista de emails (.txt, .json ou .csv)')
    parser.add_argument('--intervalo', type=float, default=1.0,
                       help='Segundos de espera entre envios (padrão: 1.0)')
    parser.add_argument('--lote', type=int, default=100,
                       help='Tamanho do lote para pausa maior (padrão: 100)')
    
    args = parser.parse_args()
    
    # Verifica configuração de email
    if not SMTP_CONFIG['user'] or not SMTP_CONFIG['password']:
        logger.error("Configurações de email não definidas")
        print("\n✗ Erro: Configurações de email não definidas")
        print("  Configure as credenciais SMTP no arquivo .env")
        print("\nVeja o guia: CONFIGURAR_GMAIL.md")
        return 1
    
    # Executa envio em massa
    enviar_em_massa(
        hash_id=args.hash_id,
        arquivo_destinatarios=args.destinatarios,
        intervalo=args.intervalo,
        lote_tamanho=args.lote
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
