"""
Gerador de Hash para Fascículos
Gera hashes únicos e verificáveis para cada fascículo
"""
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import PyPDF2


class HashGenerator:
    """Gera hashes únicos para fascículos"""
    
    def __init__(self, algorithm: str = 'sha256'):
        self.algorithm = algorithm
    
    def generate_fasciculo_hash(
        self,
        pdf_path: Path,
        edicao: str,
        fasciculo: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Gera um hash único para um fascículo
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            edicao: Nome/número da edição
            fasciculo: Nome/número do fascículo
            metadata: Metadados adicionais (opcional)
        
        Returns:
            Dicionário com informações do hash gerado
        """
        # Gera ID único
        hash_id = str(uuid.uuid4())
        
        # Lê o conteúdo do PDF
        pdf_content = self._read_pdf_content(pdf_path)
        
        # Obtém metadados do PDF
        pdf_metadata = self._extract_pdf_metadata(pdf_path)
        
        # Cria string única para hash
        unique_string = f"{hash_id}|{edicao}|{fasciculo}|{pdf_content}|{datetime.utcnow().isoformat()}"
        
        # Gera hash
        hash_object = hashlib.new(self.algorithm)
        hash_object.update(unique_string.encode('utf-8'))
        fasciculo_hash = hash_object.hexdigest()
        
        # Retorna informações completas
        return {
            'hash_id': hash_id,
            'fasciculo_hash': fasciculo_hash,
            'edicao': edicao,
            'fasciculo': fasciculo,
            'pdf_path': str(pdf_path),
            'pdf_size': pdf_path.stat().st_size,
            'pdf_metadata': pdf_metadata,
            'timestamp': datetime.utcnow().isoformat(),
            'algorithm': self.algorithm,
            'metadata': metadata or {}
        }
    
    def _read_pdf_content(self, pdf_path: Path) -> str:
        """Lê e retorna hash do conteúdo do PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
                
                # Retorna hash do conteúdo para não armazenar texto completo
                hash_obj = hashlib.sha256(content.encode('utf-8'))
                return hash_obj.hexdigest()
        except Exception as e:
            print(f"Erro ao ler PDF: {e}")
            # Em caso de erro, usa hash do arquivo binário
            with open(pdf_path, 'rb') as file:
                hash_obj = hashlib.sha256(file.read())
                return hash_obj.hexdigest()
    
    def _extract_pdf_metadata(self, pdf_path: Path) -> Dict:
        """Extrai metadados do PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'num_pages': len(pdf_reader.pages)
                }
        except Exception as e:
            print(f"Erro ao extrair metadados: {e}")
            return {}
    
    def verify_hash(self, pdf_path: Path, original_hash: str) -> bool:
        """
        Verifica se o hash de um PDF corresponde ao hash original
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            original_hash: Hash original para comparação
        
        Returns:
            True se os hashes correspondem, False caso contrário
        """
        current_content_hash = self._read_pdf_content(pdf_path)
        return current_content_hash in original_hash


if __name__ == "__main__":
    # Teste do gerador de hash
    generator = HashGenerator()
    
    # Exemplo de uso
    print("=== Gerador de Hash para Fascículos ===")
    print("Exemplo de hash gerado:")
    
    # Simula geração de hash (sem PDF real)
    test_hash = {
        'hash_id': str(uuid.uuid4()),
        'fasciculo_hash': hashlib.sha256(b"test").hexdigest(),
        'edicao': 'Edição 001',
        'fasciculo': 'Fascículo 01',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    for key, value in test_hash.items():
        print(f"  {key}: {value}")
