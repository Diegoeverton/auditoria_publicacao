"""
Script de Backup Automático
Faz backup de todos os arquivos críticos do sistema
"""
import shutil
import os
from datetime import datetime
from pathlib import Path

# Configuração
BACKUP_DIR = Path("backups")
DATA_DIR = Path("data")

def create_backup():
    """Cria backup completo do sistema"""
    
    # Criar diretório de backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("BACKUP DO SISTEMA DE AUDITORIA")
    print("=" * 70)
    print(f"\nCriando backup em: {backup_path}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    files_backed_up = 0
    
    # Backup da blockchain
    blockchain_file = DATA_DIR / "blockchain.json"
    if blockchain_file.exists():
        shutil.copy2(blockchain_file, backup_path / "blockchain.json")
        size_kb = blockchain_file.stat().st_size / 1024
        print(f"[OK] Blockchain copiada ({size_kb:.2f} KB)")
        files_backed_up += 1
    else:
        print("[AVISO] Blockchain não encontrada")
    
    # Backup da chave de criptografia
    key_file = DATA_DIR / "keys" / "encryption.key"
    if key_file.exists():
        (backup_path / "keys").mkdir(exist_ok=True)
        shutil.copy2(key_file, backup_path / "keys" / "encryption.key")
        print("[OK] Chave de criptografia copiada (CRÍTICO!)")
        files_backed_up += 1
    else:
        print("[AVISO] Chave de criptografia não encontrada")
    
    # Backup dos hashes
    hash_files = list(DATA_DIR.glob("hash_*.json"))
    if hash_files:
        for hash_file in hash_files:
            shutil.copy2(hash_file, backup_path / hash_file.name)
        print(f"[OK] {len(hash_files)} arquivo(s) de hash copiados")
        files_backed_up += len(hash_files)
    else:
        print("ℹ Nenhum arquivo de hash encontrado")
    
    # Backup do .env (se existir)
    env_file = Path(".env")
    if env_file.exists():
        shutil.copy2(env_file, backup_path / ".env")
        print("[OK] Arquivo .env copiado")
        files_backed_up += 1
    
    print(f"\n[OK] Backup concluído com sucesso!")
    print(f"  Local: {backup_path}")
    print(f"  Total de arquivos: {files_backed_up}")
    
    # Calcular tamanho total do backup
    total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
    print(f"  Tamanho total: {total_size / 1024:.2f} KB")
    
    return backup_path


def cleanup_old_backups(days_to_keep=30):
    """Remove backups mais antigos que X dias"""
    
    print(f"\nLimpando backups antigos (mantendo últimos {days_to_keep} dias)...")
    
    if not BACKUP_DIR.exists():
        print("ℹ Nenhum backup antigo encontrado")
        return
    
    import time
    removed_count = 0
    
    for old_backup in BACKUP_DIR.iterdir():
        if old_backup.is_dir():
            age_days = (time.time() - old_backup.stat().st_mtime) / 86400
            if age_days > days_to_keep:
                shutil.rmtree(old_backup)
                print(f"[OK] Backup antigo removido: {old_backup.name} ({age_days:.0f} dias)")
                removed_count += 1
    
    if removed_count == 0:
        print("ℹ Nenhum backup antigo para remover")
    else:
        print(f"[OK] {removed_count} backup(s) antigo(s) removido(s)")


def list_backups():
    """Lista todos os backups disponíveis"""
    
    print("\n" + "=" * 70)
    print("BACKUPS DISPONÍVEIS")
    print("=" * 70)
    
    if not BACKUP_DIR.exists() or not list(BACKUP_DIR.iterdir()):
        print("\nℹ Nenhum backup encontrado")
        return
    
    backups = sorted(BACKUP_DIR.iterdir(), reverse=True)
    
    print(f"\nTotal de backups: {len(backups)}\n")
    
    for backup in backups:
        if backup.is_dir():
            # Calcular tamanho
            total_size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
            
            # Calcular idade
            import time
            age_days = (time.time() - backup.stat().st_mtime) / 86400
            
            # Contar arquivos
            file_count = len(list(backup.rglob('*')))
            
            print(f"📁 {backup.name}")
            print(f"   Tamanho: {total_size / 1024:.2f} KB")
            print(f"   Arquivos: {file_count}")
            print(f"   Idade: {age_days:.1f} dias")
            print()


if __name__ == "__main__":
    import sys
    
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  SISTEMA DE BACKUP - AUDITORIA DE PUBLICAÇÃO".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    try:
        # Criar backup
        backup_path = create_backup()
        
        # Limpar backups antigos
        cleanup_old_backups(days_to_keep=30)
        
        # Listar backups
        list_backups()
        
        print("\n" + "=" * 70)
        print("BACKUP CONCLUÍDO COM SUCESSO")
        print("=" * 70)
        print(f"\n[AVISO] IMPORTANTE: Guarde o backup em local seguro!")
        print(f"  Especialmente: {backup_path / 'keys' / 'encryption.key'}")
        print(f"\n💡 DICA: Copie o backup para um disco externo ou nuvem")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante backup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
