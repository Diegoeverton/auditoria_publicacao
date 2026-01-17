"""
Gerenciador de Banco de Dados MySQL
Responsável por armazenar logs e hashes no banco de dados
"""
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class DatabaseManager:
    """Gerencia conexão e operações com MySQL"""
    
    def __init__(self):
        """Inicializa conexão com banco de dados"""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'auditoria_publicacao'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
            'autocommit': True
        }
        self.connection = None
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"✓ Conectado ao MySQL: {self.config['database']}")
                return True
        except Error as e:
            print(f"✗ Erro ao conectar ao MySQL: {e}")
            return False
    
    def disconnect(self):
        """Fecha conexão com o banco de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Conexão com MySQL encerrada")
    
    def create_tables(self):
        """Cria tabelas necessárias se não existirem"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        cursor = self.connection.cursor()
        
        try:
            # Tabela de fascículos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fasciculos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hash_id VARCHAR(255) UNIQUE NOT NULL,
                    edicao VARCHAR(255) NOT NULL,
                    fasciculo VARCHAR(255) NOT NULL,
                    fasciculo_hash VARCHAR(255) NOT NULL,
                    pdf_path TEXT,
                    pdf_size BIGINT,
                    algorithm VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_hash_id (hash_id),
                    INDEX idx_edicao (edicao),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela de logs de eventos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs_eventos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hash_id VARCHAR(255) NOT NULL,
                    evento_tipo ENUM('HASH_GENERATED', 'HASH_ENCRYPTED', 'HASH_DECRYPTED', 'EMAIL_SENT', 'VERIFICATION') NOT NULL,
                    destinatario VARCHAR(255),
                    nome_destinatario VARCHAR(255),
                    dados_adicionais JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_hash_id (hash_id),
                    INDEX idx_evento_tipo (evento_tipo),
                    INDEX idx_destinatario (destinatario),
                    INDEX idx_created_at (created_at),
                    FOREIGN KEY (hash_id) REFERENCES fasciculos(hash_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela de envios em massa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS envios_massa (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    hash_id VARCHAR(255) NOT NULL,
                    total_destinatarios INT NOT NULL,
                    enviados INT DEFAULT 0,
                    erros INT DEFAULT 0,
                    tempo_total_minutos DECIMAL(10,2),
                    status ENUM('EM_ANDAMENTO', 'CONCLUIDO', 'ERRO') DEFAULT 'EM_ANDAMENTO',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    INDEX idx_hash_id (hash_id),
                    INDEX idx_status (status),
                    FOREIGN KEY (hash_id) REFERENCES fasciculos(hash_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            print("✓ Tabelas criadas/verificadas com sucesso")
            return True
            
        except Error as e:
            print(f"✗ Erro ao criar tabelas: {e}")
            return False
        finally:
            cursor.close()
    
    def inserir_fasciculo(self, hash_info: Dict[str, Any]) -> bool:
        """
        Insere informações de um fascículo no banco
        
        Args:
            hash_info: Dicionário com informações do hash
        
        Returns:
            True se inserido com sucesso, False caso contrário
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        cursor = self.connection.cursor()
        
        try:
            query = """
                INSERT INTO fasciculos 
                (hash_id, edicao, fasciculo, fasciculo_hash, pdf_path, pdf_size, algorithm)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                hash_info['hash_id'],
                hash_info['edicao'],
                hash_info['fasciculo'],
                hash_info['fasciculo_hash'],
                hash_info.get('pdf_path', ''),
                hash_info.get('pdf_size', 0),
                hash_info.get('algorithm', 'sha256')
            )
            
            cursor.execute(query, values)
            print(f"✓ Fascículo inserido no banco: {hash_info['hash_id']}")
            return True
            
        except Error as e:
            print(f"✗ Erro ao inserir fascículo: {e}")
            return False
        finally:
            cursor.close()
    
    def inserir_log_evento(self, hash_id: str, evento_tipo: str, 
                          destinatario: Optional[str] = None,
                          nome_destinatario: Optional[str] = None,
                          dados_adicionais: Optional[Dict] = None) -> bool:
        """
        Insere log de evento no banco
        
        Args:
            hash_id: ID do hash do fascículo
            evento_tipo: Tipo do evento
            destinatario: Email do destinatário (opcional)
            nome_destinatario: Nome do destinatário (opcional)
            dados_adicionais: Dados extras em formato JSON (opcional)
        
        Returns:
            True se inserido com sucesso, False caso contrário
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        cursor = self.connection.cursor()
        
        try:
            query = """
                INSERT INTO logs_eventos 
                (hash_id, evento_tipo, destinatario, nome_destinatario, dados_adicionais)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            dados_json = json.dumps(dados_adicionais) if dados_adicionais else None
            
            values = (
                hash_id,
                evento_tipo,
                destinatario,
                nome_destinatario,
                dados_json
            )
            
            cursor.execute(query, values)
            return True
            
        except Error as e:
            print(f"✗ Erro ao inserir log de evento: {e}")
            return False
        finally:
            cursor.close()
    
    def buscar_fasciculo(self, hash_id: str) -> Optional[Dict]:
        """
        Busca informações de um fascículo pelo hash_id
        
        Args:
            hash_id: ID do hash do fascículo
        
        Returns:
            Dicionário com informações do fascículo ou None
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = "SELECT * FROM fasciculos WHERE hash_id = %s"
            cursor.execute(query, (hash_id,))
            result = cursor.fetchone()
            return result
            
        except Error as e:
            print(f"✗ Erro ao buscar fascículo: {e}")
            return None
        finally:
            cursor.close()
    
    def buscar_logs_fasciculo(self, hash_id: str) -> List[Dict]:
        """
        Busca todos os logs de um fascículo
        
        Args:
            hash_id: ID do hash do fascículo
        
        Returns:
            Lista de dicionários com logs
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT * FROM logs_eventos 
                WHERE hash_id = %s 
                ORDER BY created_at ASC
            """
            cursor.execute(query, (hash_id,))
            results = cursor.fetchall()
            
            # Converte JSON de volta para dict
            for result in results:
                if result['dados_adicionais']:
                    result['dados_adicionais'] = json.loads(result['dados_adicionais'])
            
            return results
            
        except Error as e:
            print(f"✗ Erro ao buscar logs: {e}")
            return []
        finally:
            cursor.close()
    
    def buscar_fasciculos_edicao(self, edicao: str) -> List[Dict]:
        """
        Busca todos os fascículos de uma edição
        
        Args:
            edicao: Nome da edição
        
        Returns:
            Lista de dicionários com fascículos
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = "SELECT * FROM fasciculos WHERE edicao = %s ORDER BY created_at ASC"
            cursor.execute(query, (edicao,))
            results = cursor.fetchall()
            return results
            
        except Error as e:
            print(f"✗ Erro ao buscar fascículos da edição: {e}")
            return []
        finally:
            cursor.close()
    
    def get_estatisticas(self) -> Dict:
        """
        Retorna estatísticas gerais do banco
        
        Returns:
            Dicionário com estatísticas
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            stats = {}
            
            # Total de fascículos
            cursor.execute("SELECT COUNT(*) as total FROM fasciculos")
            stats['total_fasciculos'] = cursor.fetchone()['total']
            
            # Total de edições únicas
            cursor.execute("SELECT COUNT(DISTINCT edicao) as total FROM fasciculos")
            stats['total_edicoes'] = cursor.fetchone()['total']
            
            # Total de emails enviados
            cursor.execute("SELECT COUNT(*) as total FROM logs_eventos WHERE evento_tipo = 'EMAIL_SENT'")
            stats['total_emails_enviados'] = cursor.fetchone()['total']
            
            # Total de logs
            cursor.execute("SELECT COUNT(*) as total FROM logs_eventos")
            stats['total_logs'] = cursor.fetchone()['total']
            
            # Logs por tipo
            cursor.execute("""
                SELECT evento_tipo, COUNT(*) as total 
                FROM logs_eventos 
                GROUP BY evento_tipo
            """)
            stats['logs_por_tipo'] = {row['evento_tipo']: row['total'] for row in cursor.fetchall()}
            
            return stats
            
        except Error as e:
            print(f"✗ Erro ao buscar estatísticas: {e}")
            return {}
        finally:
            cursor.close()


if __name__ == "__main__":
    # Teste do gerenciador de banco de dados
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 70)
    print("TESTE DO GERENCIADOR DE BANCO DE DADOS")
    print("=" * 70)
    
    db = DatabaseManager()
    
    # Conectar
    print("\n[1/3] Conectando ao banco...")
    if db.connect():
        print("  ✓ Conexão estabelecida")
    else:
        print("  ✗ Falha na conexão")
        print("\n⚠ Certifique-se de que:")
        print("  1. MySQL está instalado e rodando")
        print("  2. Arquivo .env está configurado corretamente")
        print("  3. Banco de dados existe (ou será criado)")
        exit(1)
    
    # Criar tabelas
    print("\n[2/3] Criando/verificando tabelas...")
    if db.create_tables():
        print("  ✓ Tabelas prontas")
    
    # Estatísticas
    print("\n[3/3] Buscando estatísticas...")
    stats = db.get_estatisticas()
    print(f"  Total de fascículos: {stats.get('total_fasciculos', 0)}")
    print(f"  Total de edições: {stats.get('total_edicoes', 0)}")
    print(f"  Total de emails enviados: {stats.get('total_emails_enviados', 0)}")
    
    # Desconectar
    db.disconnect()
    
    print("\n✓ Teste concluído!")
