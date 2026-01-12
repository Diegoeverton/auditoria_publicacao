"""
Configurações do Sistema de Auditoria de Publicação
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KEYS_DIR = DATA_DIR / "keys"
FASCICULOS_DIR = BASE_DIR / "fasciculos"

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
KEYS_DIR.mkdir(exist_ok=True)
FASCICULOS_DIR.mkdir(exist_ok=True)

# Configurações de Email
SMTP_CONFIG = {
    'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'user': os.getenv('SMTP_USER', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'from': os.getenv('EMAIL_FROM', '')
}

# Configurações de Criptografia
ENCRYPTION_KEY_PATH = KEYS_DIR / "encryption.key"

# Configurações de Blockchain
BLOCKCHAIN_PATH = DATA_DIR / "blockchain.json"

# Configurações de Hash
HASH_ALGORITHM = 'sha256'
