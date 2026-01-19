"""
Script para corrigir caracteres Unicode para ASCII compatível com Windows
"""
import os
from pathlib import Path

# Mapeamento de caracteres Unicode para ASCII
replacements = {
    '[OK]': '[OK]',
    '[ERRO]': '[ERRO]',
    '[AVISO]': '[AVISO]',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
    '': '',
}

def fix_file(filepath):
    """Corrige caracteres Unicode em um arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for unicode_char, ascii_char in replacements.items():
            content = content.replace(unicode_char, ascii_char)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Corrigido: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao processar {filepath}: {e}")
        return False

def main():
    """Processa todos os arquivos Python"""
    print("=" * 70)
    print("CORRIGINDO CARACTERES UNICODE PARA ASCII")
    print("=" * 70)
    
    # Diretórios para processar
    dirs_to_process = ['src', '.']
    files_fixed = 0
    
    for dir_path in dirs_to_process:
        dir_full_path = Path(dir_path)
        if not dir_full_path.exists():
            continue
        
        # Processar arquivos .py
        for py_file in dir_full_path.glob('*.py'):
            if fix_file(py_file):
                files_fixed += 1
    
    print("\n" + "=" * 70)
    print(f"[OK] {files_fixed} arquivo(s) corrigido(s)")
    print("=" * 70)

if __name__ == "__main__":
    main()
