"""
Sistema de Logging Centralizado
Configuração de logs para todo o sistema
"""
import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


class LoggerConfig:
    """Configuração centralizada de logging"""
    
    _instance = None
    _configured = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._configured:
            self.setup_logging()
            self._configured = True
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        
        # Criar diretório de logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Arquivo de log principal
        log_file = log_dir / f"auditoria_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configuração do formato
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo (com rotação)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=30,  # Manter últimos 30 arquivos
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        
        # Configurar logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remover handlers existentes
        root_logger.handlers.clear()
        
        # Adicionar handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Log inicial
        logging.info("=" * 70)
        logging.info("Sistema de Logging Inicializado")
        logging.info(f"Arquivo de log: {log_file}")
        logging.info("=" * 70)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Retorna um logger configurado
        
        Args:
            name: Nome do logger (geralmente __name__)
        
        Returns:
            Logger configurado
        """
        return logging.getLogger(name)


# Inicializar logging ao importar
logger_config = LoggerConfig()


# Função helper para facilitar uso
def get_logger(name: str = __name__) -> logging.Logger:
    """
    Retorna um logger configurado
    
    Args:
        name: Nome do logger
    
    Returns:
        Logger configurado
    """
    return LoggerConfig.get_logger(name)


if __name__ == "__main__":
    # Teste do sistema de logging
    logger = get_logger(__name__)
    
    logger.debug("Mensagem de debug")
    logger.info("Mensagem de informação")
    logger.warning("Mensagem de aviso")
    logger.error("Mensagem de erro")
    
    try:
        1 / 0
    except Exception as e:
        logger.exception("Erro capturado com stack trace:")
    
    print("\n[OK] Sistema de logging testado com sucesso!")
    print("Verifique o arquivo em: logs/auditoria_*.log")
