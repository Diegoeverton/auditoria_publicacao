"""
Módulo de Validações
Valida entradas do sistema para garantir segurança e integridade
"""
import re
from pathlib import Path
from typing import Tuple, Optional
import os


class Validator:
    """Classe para validações de entrada"""
    
    # Regex para validar email
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Tamanho máximo de PDF para email (25 MB)
    MAX_PDF_SIZE_MB = 25
    MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024
    
    # Caracteres não permitidos em nomes
    INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de email
        
        Args:
            email: Email a ser validado
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not email:
            return False, "Email não pode ser vazio"
        
        if not isinstance(email, str):
            return False, "Email deve ser uma string"
        
        email = email.strip()
        
        if len(email) > 254:  # RFC 5321
            return False, "Email muito longo (máximo 254 caracteres)"
        
        if not Validator.EMAIL_REGEX.match(email):
            return False, f"Formato de email inválido: {email}"
        
        return True, None
    
    @staticmethod
    def validar_pdf(pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        Valida arquivo PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not pdf_path:
            return False, "Caminho do PDF não pode ser vazio"
        
        path = Path(pdf_path)
        
        # Verificar se arquivo existe
        if not path.exists():
            return False, f"Arquivo PDF não encontrado: {pdf_path}"
        
        # Verificar se é arquivo (não diretório)
        if not path.is_file():
            return False, f"Caminho não é um arquivo: {pdf_path}"
        
        # Verificar extensão
        if path.suffix.lower() != '.pdf':
            return False, f"Arquivo não é PDF: {pdf_path} (extensão: {path.suffix})"
        
        # Verificar tamanho
        size_bytes = path.stat().st_size
        if size_bytes == 0:
            return False, f"Arquivo PDF está vazio: {pdf_path}"
        
        if size_bytes > Validator.MAX_PDF_SIZE_BYTES:
            size_mb = size_bytes / (1024 * 1024)
            return False, f"PDF muito grande: {size_mb:.2f} MB (máximo: {Validator.MAX_PDF_SIZE_MB} MB)"
        
        # Verificar se é realmente um PDF (magic bytes)
        try:
            with open(path, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    return False, f"Arquivo não é um PDF válido: {pdf_path}"
        except Exception as e:
            return False, f"Erro ao ler arquivo PDF: {e}"
        
        return True, None
    
    @staticmethod
    def validar_nome(nome: str, campo: str = "Nome") -> Tuple[bool, Optional[str]]:
        """
        Valida nome de edição/fascículo
        
        Args:
            nome: Nome a ser validado
            campo: Nome do campo (para mensagem de erro)
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not nome:
            return False, f"{campo} não pode ser vazio"
        
        if not isinstance(nome, str):
            return False, f"{campo} deve ser uma string"
        
        nome = nome.strip()
        
        if len(nome) == 0:
            return False, f"{campo} não pode conter apenas espaços"
        
        if len(nome) > 255:
            return False, f"{campo} muito longo (máximo 255 caracteres)"
        
        # Verificar caracteres inválidos
        if re.search(Validator.INVALID_CHARS, nome):
            return False, f"{campo} contém caracteres inválidos: {nome}"
        
        return True, None
    
    @staticmethod
    def validar_hash_id(hash_id: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de hash ID (UUID)
        
        Args:
            hash_id: Hash ID a ser validado
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not hash_id:
            return False, "Hash ID não pode ser vazio"
        
        if not isinstance(hash_id, str):
            return False, "Hash ID deve ser uma string"
        
        hash_id = hash_id.strip()
        
        # Formato UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        uuid_regex = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        
        if not uuid_regex.match(hash_id):
            return False, f"Formato de Hash ID inválido: {hash_id}"
        
        return True, None
    
    @staticmethod
    def sanitizar_sql(texto: str) -> str:
        """
        Sanitiza texto para prevenir SQL injection
        
        Args:
            texto: Texto a ser sanitizado
        
        Returns:
            Texto sanitizado
        """
        if not texto:
            return texto
        
        # Remove caracteres perigosos
        texto = texto.replace("'", "''")  # Escape aspas simples
        texto = texto.replace(";", "")    # Remove ponto e vírgula
        texto = texto.replace("--", "")   # Remove comentários SQL
        texto = texto.replace("/*", "")   # Remove comentários SQL
        texto = texto.replace("*/", "")   # Remove comentários SQL
        
        return texto
    
    @staticmethod
    def validar_intervalo(intervalo: float) -> Tuple[bool, Optional[str]]:
        """
        Valida intervalo de tempo entre envios
        
        Args:
            intervalo: Intervalo em segundos
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not isinstance(intervalo, (int, float)):
            return False, "Intervalo deve ser um número"
        
        if intervalo < 0:
            return False, "Intervalo não pode ser negativo"
        
        if intervalo > 60:
            return False, "Intervalo muito grande (máximo 60 segundos)"
        
        return True, None
    
    @staticmethod
    def validar_lote(lote: int) -> Tuple[bool, Optional[str]]:
        """
        Valida tamanho de lote para envio em massa
        
        Args:
            lote: Tamanho do lote
        
        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not isinstance(lote, int):
            return False, "Tamanho do lote deve ser um número inteiro"
        
        if lote < 1:
            return False, "Tamanho do lote deve ser pelo menos 1"
        
        if lote > 500:
            return False, "Tamanho do lote muito grande (máximo 500)"
        
        return True, None


def validar_ou_erro(validacao_func, *args, **kwargs):
    """
    Helper para validar e levantar exceção se inválido
    
    Args:
        validacao_func: Função de validação
        *args: Argumentos para a função
        **kwargs: Argumentos nomeados para a função
    
    Raises:
        ValueError: Se validação falhar
    """
    valido, erro = validacao_func(*args, **kwargs)
    if not valido:
        raise ValueError(erro)


if __name__ == "__main__":
    # Testes de validação
    print("=" * 70)
    print("TESTES DE VALIDAÇÃO")
    print("=" * 70)
    
    # Teste de email
    print("\n1. Validação de Email:")
    emails_teste = [
        "usuario@exemplo.com",
        "invalido@",
        "sem-arroba.com",
        "usuario@exemplo",
        ""
    ]
    
    for email in emails_teste:
        valido, erro = Validator.validar_email(email)
        status = "✓" if valido else "✗"
        print(f"  {status} {email:30s} - {erro or 'Válido'}")
    
    # Teste de PDF
    print("\n2. Validação de PDF:")
    pdfs_teste = [
        "fasciculos/demo_fasciculo.pdf",
        "arquivo_inexistente.pdf",
        "README.md"
    ]
    
    for pdf in pdfs_teste:
        valido, erro = Validator.validar_pdf(pdf)
        status = "✓" if valido else "✗"
        print(f"  {status} {pdf:30s} - {erro or 'Válido'}")
    
    # Teste de nome
    print("\n3. Validação de Nome:")
    nomes_teste = [
        "Edição 001",
        "Fascículo <script>",
        "",
        "Nome válido com espaços"
    ]
    
    for nome in nomes_teste:
        valido, erro = Validator.validar_nome(nome, "Edição")
        status = "✓" if valido else "✗"
        print(f"  {status} {nome:30s} - {erro or 'Válido'}")
    
    print("\n✓ Testes de validação concluídos!")
