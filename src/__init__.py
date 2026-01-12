"""
Sistema de Auditoria de Publicação de Fascículos
Módulo principal com componentes de hash, criptografia, blockchain e email
"""

__version__ = "1.0.0"
__author__ = "Sistema de Auditoria"

from .hash_generator import HashGenerator
from .crypto_manager import CryptoManager
from .blockchain_audit import BlockchainAudit, BlockType, Block
from .email_sender import EmailSender

__all__ = [
    'HashGenerator',
    'CryptoManager',
    'BlockchainAudit',
    'BlockType',
    'Block',
    'EmailSender'
]
