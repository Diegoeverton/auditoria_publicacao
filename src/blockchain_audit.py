"""
Sistema de Auditoria Blockchain
Mantém uma cadeia imutável de registros de todas as operações
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class BlockType(Enum):
    """Tipos de blocos na blockchain"""
    GENESIS = "GENESIS"
    HASH_GENERATED = "HASH_GENERATED"
    HASH_ENCRYPTED = "HASH_ENCRYPTED"
    HASH_DECRYPTED = "HASH_DECRYPTED"
    EMAIL_SENT = "EMAIL_SENT"
    VERIFICATION = "VERIFICATION"


class Block:
    """Representa um bloco na blockchain de auditoria"""
    
    def __init__(
        self,
        index: int,
        timestamp: str,
        data: Dict[str, Any],
        previous_hash: str,
        block_type: BlockType
    ):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.block_type = block_type.value
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcula o hash do bloco"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'block_type': self.block_type
        }, sort_keys=True, ensure_ascii=False)
        
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict:
        """Converte o bloco para dicionário"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'block_type': self.block_type,
            'hash': self.hash
        }


class BlockchainAudit:
    """Sistema de auditoria baseado em blockchain"""
    
    def __init__(self, blockchain_path: Path):
        """
        Inicializa a blockchain de auditoria
        
        Args:
            blockchain_path: Caminho para o arquivo da blockchain
        """
        self.blockchain_path = blockchain_path
        self.chain: List[Block] = []
        self._load_or_create_blockchain()
    
    def _load_or_create_blockchain(self):
        """Carrega blockchain existente ou cria uma nova"""
        if self.blockchain_path.exists():
            self._load_blockchain()
        else:
            self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Cria o bloco gênesis (primeiro bloco)"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            data={
                'message': 'Bloco Gênesis - Sistema de Auditoria de Publicação',
                'version': '1.0',
                'created': datetime.utcnow().isoformat()
            },
            previous_hash='0',
            block_type=BlockType.GENESIS
        )
        
        self.chain.append(genesis_block)
        self._save_blockchain()
        print(f"[OK] Blockchain criada com bloco gênesis")
    
    def _load_blockchain(self):
        """Carrega blockchain do arquivo"""
        try:
            with open(self.blockchain_path, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)
            
            for block_data in chain_data:
                block = Block(
                    index=block_data['index'],
                    timestamp=block_data['timestamp'],
                    data=block_data['data'],
                    previous_hash=block_data['previous_hash'],
                    block_type=BlockType(block_data['block_type'])
                )
                # Verifica se o hash está correto
                if block.hash == block_data['hash']:
                    self.chain.append(block)
                else:
                    raise ValueError(f"Hash inválido no bloco {block_data['index']}")
            
            print(f"[OK] Blockchain carregada: {len(self.chain)} blocos")
        except Exception as e:
            print(f"Erro ao carregar blockchain: {e}")
            print("Criando nova blockchain...")
            self._create_genesis_block()
    
    def _save_blockchain(self):
        """Salva blockchain no arquivo"""
        self.blockchain_path.parent.mkdir(parents=True, exist_ok=True)
        
        chain_data = [block.to_dict() for block in self.chain]
        
        with open(self.blockchain_path, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2, ensure_ascii=False)
    
    def add_block(self, data: Dict[str, Any], block_type: BlockType) -> Block:
        """
        Adiciona um novo bloco à blockchain
        
        Args:
            data: Dados a serem armazenados no bloco
            block_type: Tipo do bloco
        
        Returns:
            Bloco criado
        """
        previous_block = self.chain[-1]
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            data=data,
            previous_hash=previous_block.hash,
            block_type=block_type
        )
        
        self.chain.append(new_block)
        self._save_blockchain()
        
        return new_block
    
    def verify_integrity(self) -> bool:
        """
        Verifica a integridade da blockchain
        
        Returns:
            True se a blockchain está íntegra, False caso contrário
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verifica se o hash do bloco atual está correto
            if current_block.hash != current_block.calculate_hash():
                print(f"[ERRO] Hash inválido no bloco {i}")
                return False
            
            # Verifica se o previous_hash está correto
            if current_block.previous_hash != previous_block.hash:
                print(f"[ERRO] Cadeia quebrada no bloco {i}")
                return False
        
        return True
    
    def get_blocks_by_hash_id(self, hash_id: str) -> List[Block]:
        """
        Retorna todos os blocos relacionados a um hash_id específico
        
        Args:
            hash_id: ID do hash para buscar
        
        Returns:
            Lista de blocos relacionados
        """
        return [
            block for block in self.chain
            if block.data.get('hash_id') == hash_id
        ]
    
    def get_blocks_by_edicao(self, edicao: str) -> List[Block]:
        """
        Retorna todos os blocos relacionados a uma edição específica
        
        Args:
            edicao: Nome da edição para buscar
        
        Returns:
            Lista de blocos relacionados
        """
        return [
            block for block in self.chain
            if block.data.get('edicao') == edicao
        ]
    
    def get_blocks_by_type(self, block_type: BlockType) -> List[Block]:
        """
        Retorna todos os blocos de um tipo específico
        
        Args:
            block_type: Tipo de bloco para buscar
        
        Returns:
            Lista de blocos do tipo especificado
        """
        return [
            block for block in self.chain
            if block.block_type == block_type.value
        ]
    
    def get_audit_trail(self, hash_id: str) -> List[Dict]:
        """
        Retorna a trilha de auditoria completa para um fascículo
        
        Args:
            hash_id: ID do hash para buscar
        
        Returns:
            Lista ordenada de eventos na trilha de auditoria
        """
        blocks = self.get_blocks_by_hash_id(hash_id)
        
        trail = []
        for block in blocks:
            trail.append({
                'timestamp': block.timestamp,
                'action': block.block_type,
                'data': block.data,
                'block_index': block.index,
                'block_hash': block.hash
            })
        
        return sorted(trail, key=lambda x: x['timestamp'])
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas da blockchain"""
        stats = {
            'total_blocks': len(self.chain),
            'blocks_by_type': {},
            'total_edicoes': set(),
            'total_fasciculos': set(),
            'total_emails_sent': 0
        }
        
        for block in self.chain:
            # Conta por tipo
            block_type = block.block_type
            stats['blocks_by_type'][block_type] = stats['blocks_by_type'].get(block_type, 0) + 1
            
            # Coleta edições e fascículos únicos
            if 'edicao' in block.data:
                stats['total_edicoes'].add(block.data['edicao'])
            if 'fasciculo' in block.data:
                stats['total_fasciculos'].add(block.data['fasciculo'])
            
            # Conta emails enviados
            if block.block_type == BlockType.EMAIL_SENT.value:
                stats['total_emails_sent'] += 1
        
        # Converte sets para contagem
        stats['total_edicoes'] = len(stats['total_edicoes'])
        stats['total_fasciculos'] = len(stats['total_fasciculos'])
        
        return stats


if __name__ == "__main__":
    # Teste da blockchain
    from config import BLOCKCHAIN_PATH
    
    blockchain = BlockchainAudit(BLOCKCHAIN_PATH)
    
    print("=== Sistema de Auditoria Blockchain ===")
    print(f"\nTotal de blocos: {len(blockchain.chain)}")
    
    # Adiciona bloco de teste
    test_block = blockchain.add_block(
        data={
            'hash_id': 'test-123',
            'edicao': 'Edição 001',
            'fasciculo': 'Fascículo 01',
            'action': 'Teste de sistema'
        },
        block_type=BlockType.HASH_GENERATED
    )
    
    print(f"\n[OK] Bloco de teste adicionado (index: {test_block.index})")
    
    # Verifica integridade
    is_valid = blockchain.verify_integrity()
    print(f"\nIntegridade da blockchain: {'[OK] VÁLIDA' if is_valid else '[ERRO] INVÁLIDA'}")
    
    # Estatísticas
    stats = blockchain.get_statistics()
    print(f"\nEstatísticas:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
