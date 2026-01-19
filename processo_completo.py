"""
Script Unificado - Sistema de Auditoria de Publicação
Integra todo o processo: Gerar Hash + Enviar em Massa + Consultar
"""
import sys
import argparse
import subprocess
from pathlib import Path
import re
import time
import os

# Detectar Python correto (venv ou sistema)
PYTHON_CMD = 'python'

def extrair_hash_id(output):
    """Extrai hash ID da saída do main.py"""
    match = re.search(r'Hash ID: ([a-f0-9-]+)', output)
    return match.group(1) if match else None

def executar_comando(comando_lista, descricao):
    """Executa um comando e retorna a saída"""
    print(f"\n{'='*70}")
    print(f"{descricao}")
    print(f"{'='*70}")
    
    result = subprocess.run(
        comando_lista,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description='Script Unificado - Gerar Hash + Enviar em Massa + Consultar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

1. Processo completo (gerar + enviar + consultar):
   python processo_completo.py --edicao "Janeiro 2026" --fasciculo "F01" 
                                --pdf "fasciculos/janeiro.pdf" 
                                --destinatarios "lista.txt"

2. Apenas enviar (hash já existe):
   python processo_completo.py --hash-id abc123-def456 --destinatarios "lista.txt"

3. Apenas consultar:
   python processo_completo.py --consultar --hash-id abc123-def456
        """
    )
    
    # Argumentos para gerar hash
    parser.add_argument('--edicao', help='Nome ou número da edição')
    parser.add_argument('--fasciculo', help='Nome ou número do fascículo')
    parser.add_argument('--pdf', help='Caminho para o arquivo PDF')
    
    # Argumentos para envio em massa
    parser.add_argument('--hash-id', help='Hash ID do fascículo (se já foi gerado)')
    parser.add_argument('--destinatarios', help='Arquivo com lista de destinatários')
    parser.add_argument('--intervalo', type=float, default=2.0, 
                       help='Intervalo entre envios em segundos (padrão: 2.0)')
    parser.add_argument('--lote', type=int, default=100,
                       help='Tamanho do lote para pausa maior (padrão: 100)')
    
    # Argumentos para consulta
    parser.add_argument('--consultar', action='store_true',
                       help='Apenas consultar auditoria (não enviar)')
    parser.add_argument('--consultar-mysql', action='store_true',
                       help='Consultar no MySQL em vez da blockchain')
    
    # Argumentos opcionais
    parser.add_argument('--skip-envio', action='store_true',
                       help='Pular envio (apenas gerar hash e consultar)')
    parser.add_argument('--skip-consulta', action='store_true',
                       help='Pular consulta final')
    
    args = parser.parse_args()
    
    hash_id = args.hash_id
    
    print("\n" + "="*70)
    print("SISTEMA UNIFICADO DE AUDITORIA DE PUBLICACAO")
    print("="*70)
    
    # MODO 1: Apenas Consultar
    if args.consultar:
        if not hash_id:
            print("\n[ERRO] Para consultar, forneca --hash-id")
            return 1
        
        script = 'consultar_db.py' if args.consultar_mysql else 'audit_query.py'
        comando = [PYTHON_CMD, script, '--hash-id', hash_id]
        
        result = executar_comando(comando, f"CONSULTANDO AUDITORIA ({script})")
        return result.returncode
    
    # MODO 2: Processo Completo ou Parcial
    
    # ETAPA 1: Gerar Hash (se necessário)
    if not hash_id:
        if not all([args.edicao, args.fasciculo, args.pdf]):
            print("\n[ERRO] Para gerar hash, forneca: --edicao, --fasciculo e --pdf")
            print("   OU forneca --hash-id se o hash ja foi gerado")
            return 1
        
        comando = [PYTHON_CMD, 'main.py', '--edicao', args.edicao, '--fasciculo', args.fasciculo, '--pdf', args.pdf]
        
        result = executar_comando(comando, "ETAPA 1/3: GERANDO HASH DO FASCICULO")
        
        if result.returncode != 0:
            print("\n[ERRO] Falha ao gerar hash")
            return 1
        
        # Extrair hash ID da saída
        hash_id = extrair_hash_id(result.stdout)
        
        if not hash_id:
            print("\n[ERRO] Nao foi possivel extrair Hash ID da saida")
            return 1
        
        print(f"\n[OK] Hash ID gerado: {hash_id}")
        time.sleep(2)
    
    # ETAPA 2: Enviar em Massa (se não for skip)
    if not args.skip_envio and args.destinatarios:
        comando = [PYTHON_CMD, 'envio_massa.py', '--hash-id', hash_id, '--destinatarios', args.destinatarios, '--intervalo', str(args.intervalo), '--lote', str(args.lote)]
        
        result = executar_comando(comando, "ETAPA 2/3: ENVIANDO EM MASSA")
        
        if result.returncode != 0:
            print("\n[AVISO] Houve erros no envio em massa")
            print("Verifique os logs para mais detalhes")
        
        time.sleep(2)
    elif not args.destinatarios and not args.skip_envio:
        print("\n[AVISO] Nenhum arquivo de destinatarios fornecido")
        print("Pulando envio em massa. Use --destinatarios para enviar")
    
    # ETAPA 3: Consultar Auditoria (se não for skip)
    if not args.skip_consulta:
        script = 'consultar_db.py' if args.consultar_mysql else 'audit_query.py'
        comando = [PYTHON_CMD, script, '--hash-id', hash_id]
        
        result = executar_comando(comando, f"ETAPA 3/3: CONSULTANDO AUDITORIA ({script})")
    
    # Resumo Final
    print("\n" + "="*70)
    print("PROCESSO CONCLUIDO")
    print("="*70)
    print(f"\nHash ID: {hash_id}")
    
    if args.destinatarios and not args.skip_envio:
        print(f"Destinatarios: {args.destinatarios}")
        print("\nPara consultar novamente:")
        print(f"  python audit_query.py --hash-id {hash_id}")
        print(f"  python consultar_db.py --hash-id {hash_id}")
    
    print("\nLogs disponiveis em: logs/auditoria_*.log")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
