"""
Script de Envio em Massa
Envia o mesmo fascículo para múltiplos destinatários de forma automatizada
"""
import sys
import time
from pathlib import Path
import json
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crypto_manager import CryptoManager
from email_sender import EmailSender
from blockchain_audit import BlockchainAudit, BlockType
from config import ENCRYPTION_KEY_PATH, BLOCKCHAIN_PATH, SMTP_CONFIG


def carregar_destinatarios(arquivo_destinatarios):
    """
    Carrega lista de destinatários de um arquivo
    
    Formatos suportados:
    - .txt: um email por linha
    - .json: lista de emails ou lista de objetos com 'email' e 'nome'
    - .csv: primeira coluna = email, segunda coluna = nome (opcional)
    """
    arquivo = Path(arquivo_destinatarios)
    
    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    
    destinatarios = []
    
    # Arquivo TXT
    if arquivo.suffix == '.txt':
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                email = linha.strip()
                if email and '@' in email:  # Validação básica
                    destinatarios.append({'email': email, 'nome': ''})
    
    # Arquivo JSON
    elif arquivo.suffix == '.json':
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Se for lista de strings
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                destinatarios = [{'email': email, 'nome': ''} for email in data]
            
            # Se for lista de objetos
            elif isinstance(data, list) and all(isinstance(x, dict) for x in data):
                destinatarios = data
    
    # Arquivo CSV
    elif arquivo.suffix == '.csv':
        import csv
        with open(arquivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Pula cabeçalho se existir
            for row in reader:
                if row and '@' in row[0]:
                    destinatarios.append({
                        'email': row[0].strip(),
                        'nome': row[1].strip() if len(row) > 1 else ''
                    })
    
    else:
        raise ValueError(f"Formato de arquivo não suportado: {arquivo.suffix}")
    
    return destinatarios


def enviar_em_massa(hash_id, arquivo_destinatarios, intervalo=1, lote_tamanho=100):
    """
    Envia o mesmo fascículo para múltiplos destinatários
    
    Args:
        hash_id: ID do hash do fascículo
        arquivo_destinatarios: Caminho para arquivo com lista de emails
        intervalo: Segundos de espera entre envios (para evitar bloqueio SMTP)
        lote_tamanho: Número de emails por lote (pausa maior entre lotes)
    """
    
    print("=" * 70)
    print("ENVIO EM MASSA DE FASCÍCULO")
    print("=" * 70)
    print(f"\nHash ID: {hash_id}")
    print(f"Arquivo de destinatários: {arquivo_destinatarios}")
    print(f"Intervalo entre envios: {intervalo}s")
    print(f"Tamanho do lote: {lote_tamanho} emails\n")
    
    # Carrega destinatários
    print("[1/5] Carregando lista de destinatários...")
    try:
        destinatarios = carregar_destinatarios(arquivo_destinatarios)
        print(f"  ✓ {len(destinatarios)} destinatário(s) carregado(s)")
    except Exception as e:
        print(f"  ✗ Erro ao carregar destinatários: {e}")
        return
    
    if len(destinatarios) == 0:
        print("  ✗ Nenhum destinatário válido encontrado")
        return
    
    # Carrega arquivo de hash
    hash_file = Path('data') / f"hash_{hash_id}.json"
    
    if not hash_file.exists():
        print(f"\n✗ Erro: Arquivo de hash não encontrado: {hash_file}")
        print(f"  Certifique-se de que o hash foi gerado usando main.py")
        return
    
    # Inicializa componentes
    print("\n[2/5] Inicializando componentes...")
    crypto = CryptoManager(ENCRYPTION_KEY_PATH)
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    email_sender = EmailSender(SMTP_CONFIG)
    print("  ✓ Componentes inicializados")
    
    # Carrega e descriptografa hash
    print("\n[3/5] Carregando informações do fascículo...")
    with open(hash_file, 'r', encoding='utf-8') as f:
        encrypted_info = json.load(f)
    
    decrypted_info = crypto.decrypt_hash(encrypted_info)
    
    print(f"  ✓ Edição: {encrypted_info['edicao']}")
    print(f"  ✓ Fascículo: {encrypted_info['fasciculo']}")
    
    # Verifica PDF
    pdf_path = Path(decrypted_info['pdf_path'])
    if not pdf_path.exists():
        print(f"\n⚠ Aviso: PDF não encontrado em {pdf_path}")
        print(f"  O email será enviado sem anexo")
        pdf_path = None
    else:
        pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ PDF encontrado ({pdf_size_mb:.2f} MB)")
    
    # Registra início do envio em massa
    print("\n[4/5] Registrando início do envio em massa...")
    blockchain.add_block(
        data={
            'hash_id': hash_id,
            'edicao': encrypted_info['edicao'],
            'fasciculo': encrypted_info['fasciculo'],
            'total_destinatarios': len(destinatarios),
            'action': 'Início de envio em massa'
        },
        block_type=BlockType.HASH_DECRYPTED
    )
    print("  ✓ Registrado na blockchain")
    
    # Envio em massa
    print("\n[5/5] Enviando para destinatários...")
    print("-" * 70)
    
    enviados = 0
    erros = 0
    inicio = time.time()
    
    for i, dest in enumerate(destinatarios, 1):
        email = dest['email']
        nome = dest.get('nome', '')
        
        # Mensagem personalizada se tiver nome
        mensagem = f"Prezado(a) {nome},\n\n" if nome else None
        
        # Mostra progresso
        print(f"[{i}/{len(destinatarios)}] Enviando para: {email}", end='')
        if nome:
            print(f" ({nome})", end='')
        print("...", end='', flush=True)
        
        try:
            # Envia email
            result = email_sender.send_fasciculo(
                destinatario=email,
                fasciculo_info=decrypted_info,
                pdf_path=pdf_path,
                mensagem_adicional=mensagem
            )
            
            if result['success']:
                print(" ✓")
                enviados += 1
                
                # Registra envio individual na blockchain
                blockchain.add_block(
                    data={
                        'hash_id': hash_id,
                        'edicao': encrypted_info['edicao'],
                        'fasciculo': encrypted_info['fasciculo'],
                        'destinatario': email,
                        'nome_destinatario': nome,
                        'fasciculo_hash': decrypted_info['fasciculo_hash'],
                        'numero_envio': i,
                        'total_envios': len(destinatarios),
                        'action': f'Email enviado ({i}/{len(destinatarios)})'
                    },
                    block_type=BlockType.EMAIL_SENT
                )
            else:
                print(f" ✗ Erro: {result.get('error', 'Desconhecido')}")
                erros += 1
        
        except Exception as e:
            print(f" ✗ Exceção: {e}")
            erros += 1
        
        # Intervalo entre envios
        if i < len(destinatarios):
            # Pausa maior a cada lote
            if i % lote_tamanho == 0:
                pausa = intervalo * 5
                print(f"\n⏸ Pausa de {pausa}s após {lote_tamanho} envios (evitar bloqueio SMTP)...")
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
    
    # Registra conclusão
    blockchain.add_block(
        data={
            'hash_id': hash_id,
            'edicao': encrypted_info['edicao'],
            'fasciculo': encrypted_info['fasciculo'],
            'total_destinatarios': len(destinatarios),
            'enviados': enviados,
            'erros': erros,
            'tempo_total_minutos': tempo_total / 60,
            'action': 'Conclusão de envio em massa'
        },
        block_type=BlockType.VERIFICATION
    )
    
    print(f"\n✓ Envio em massa registrado na blockchain")
    print(f"\nPara consultar a auditoria:")
    print(f"  python audit_query.py --hash-id {hash_id}")


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
        print("\n✗ Erro: Configurações de email não definidas")
        print("  Configure as credenciais SMTP no arquivo .env")
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
