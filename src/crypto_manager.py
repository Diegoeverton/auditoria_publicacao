"""
Gerenciador de Criptografia
Responsável por criptografar e descriptografar hashes
"""
import json
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet
import base64


class CryptoManager:
    """Gerencia criptografia e descriptografia de dados"""
    
    def __init__(self, key_path: Path):
        """
        Inicializa o gerenciador de criptografia
        
        Args:
            key_path: Caminho para armazenar/carregar a chave de criptografia
        """
        self.key_path = key_path
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Carrega chave existente ou cria uma nova"""
        if self.key_path.exists():
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            # Gera nova chave
            key = Fernet.generate_key()
            
            # Salva a chave
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            
            print(f"✓ Nova chave de criptografia gerada em: {self.key_path}")
            return key
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """
        Criptografa um dicionário de dados
        
        Args:
            data: Dicionário com dados a serem criptografados
        
        Returns:
            String com dados criptografados (base64)
        """
        # Converte dicionário para JSON
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Criptografa
        encrypted = self.cipher.encrypt(json_data.encode('utf-8'))
        
        # Retorna como string base64
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Descriptografa dados
        
        Args:
            encrypted_data: String com dados criptografados (base64)
        
        Returns:
            Dicionário com dados descriptografados
        """
        try:
            # Decodifica base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Descriptografa
            decrypted = self.cipher.decrypt(encrypted_bytes)
            
            # Converte JSON de volta para dicionário
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Erro ao descriptografar dados: {e}")
    
    def encrypt_hash(self, hash_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Criptografa informações de hash de um fascículo
        
        Args:
            hash_info: Dicionário com informações do hash
        
        Returns:
            Dicionário com hash criptografado e metadados
        """
        # Dados sensíveis a serem criptografados
        sensitive_data = {
            'fasciculo_hash': hash_info['fasciculo_hash'],
            'pdf_path': hash_info['pdf_path'],
            'pdf_metadata': hash_info.get('pdf_metadata', {})
        }
        
        # Criptografa
        encrypted = self.encrypt_data(sensitive_data)
        
        # Retorna com dados não sensíveis em claro
        return {
            'hash_id': hash_info['hash_id'],
            'edicao': hash_info['edicao'],
            'fasciculo': hash_info['fasciculo'],
            'encrypted_data': encrypted,
            'timestamp': hash_info['timestamp'],
            'algorithm': hash_info['algorithm'],
            'is_encrypted': True
        }
    
    def decrypt_hash(self, encrypted_hash_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Descriptografa informações de hash de um fascículo
        
        Args:
            encrypted_hash_info: Dicionário com hash criptografado
        
        Returns:
            Dicionário com todas as informações descriptografadas
        """
        if not encrypted_hash_info.get('is_encrypted', False):
            return encrypted_hash_info
        
        # Descriptografa dados sensíveis
        decrypted_data = self.decrypt_data(encrypted_hash_info['encrypted_data'])
        
        # Combina com dados não sensíveis
        result = {
            'hash_id': encrypted_hash_info['hash_id'],
            'edicao': encrypted_hash_info['edicao'],
            'fasciculo': encrypted_hash_info['fasciculo'],
            'timestamp': encrypted_hash_info['timestamp'],
            'algorithm': encrypted_hash_info['algorithm'],
            **decrypted_data
        }
        
        return result
    
    def generate_signature(self, data: str) -> str:
        """
        Gera uma assinatura digital para os dados
        
        Args:
            data: String com dados a serem assinados
        
        Returns:
            Assinatura em formato hexadecimal
        """
        import hashlib
        signature = hashlib.sha256(f"{data}{self.key.decode('utf-8')}".encode('utf-8'))
        return signature.hexdigest()


if __name__ == "__main__":
    # Teste do gerenciador de criptografia
    from config import ENCRYPTION_KEY_PATH
    
    crypto = CryptoManager(ENCRYPTION_KEY_PATH)
    
    print("=== Gerenciador de Criptografia ===")
    
    # Teste de criptografia/descriptografia
    test_data = {
        'hash_id': 'test-123',
        'fasciculo_hash': 'abc123def456',
        'edicao': 'Edição 001',
        'fasciculo': 'Fascículo 01',
        'pdf_path': '/path/to/file.pdf',
        'timestamp': '2026-01-12T19:00:00',
        'algorithm': 'sha256'
    }
    
    print("\n1. Dados originais:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    print("\n2. Criptografando...")
    encrypted = crypto.encrypt_hash(test_data)
    print(f"Dados criptografados (primeiros 100 chars): {encrypted['encrypted_data'][:100]}...")
    
    print("\n3. Descriptografando...")
    decrypted = crypto.decrypt_hash(encrypted)
    print(json.dumps(decrypted, indent=2, ensure_ascii=False))
    
    print("\n✓ Teste concluído com sucesso!")
