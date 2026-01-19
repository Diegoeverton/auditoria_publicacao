"""
Migração: Adicionar tabela envios_individuais
Cria tabela para armazenar hash único para cada envio individual (fascículo + destinatário)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

def migrate():
    """Executa a migração"""
    db = DatabaseManager()
    
    print("\n[1/3] Conectando ao banco de dados...")
    if not db.connect():
        print("[ERRO] Nao foi possivel conectar ao banco")
        return False
    
    cursor = db.connection.cursor()
    
    try:
        print("\n[2/3] Criando tabela envios_individuais...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS envios_individuais (
                id INT AUTO_INCREMENT PRIMARY KEY,
                
                -- Hash do fascículo original
                hash_fasciculo VARCHAR(255) NOT NULL,
                
                -- Hash ÚNICO deste envio específico
                hash_envio VARCHAR(255) UNIQUE NOT NULL,
                
                -- Informações do destinatário
                destinatario_email VARCHAR(255) NOT NULL,
                destinatario_nome VARCHAR(255),
                
                -- Informações do envio
                status ENUM('PENDENTE', 'ENVIADO', 'ERRO', 'CONFIRMADO') DEFAULT 'PENDENTE',
                data_envio TIMESTAMP NULL,
                data_confirmacao TIMESTAMP NULL,
                
                -- Hash de verificação (SHA-256 de: hash_fasciculo + email + timestamp)
                hash_verificacao VARCHAR(255) NOT NULL,
                
                -- Metadados
                ip_envio VARCHAR(50),
                user_agent TEXT,
                dados_adicionais JSON,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                -- Índices
                INDEX idx_hash_fasciculo (hash_fasciculo),
                INDEX idx_hash_envio (hash_envio),
                INDEX idx_destinatario (destinatario_email),
                INDEX idx_status (status),
                INDEX idx_data_envio (data_envio),
                
                -- Chave estrangeira
                FOREIGN KEY (hash_fasciculo) REFERENCES fasciculos(hash_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        print("[OK] Tabela envios_individuais criada com sucesso")
        
        print("\n[3/3] Confirmando alteracoes...")
        db.connection.commit()
        
        # Verificar se a tabela foi criada
        cursor.execute("SHOW TABLES LIKE 'envios_individuais'")
        result = cursor.fetchone()
        
        if result:
            print("[OK] Tabela verificada e confirmada")
            
            # Mostrar estrutura da tabela
            print("\nEstrutura da tabela:")
            cursor.execute("DESCRIBE envios_individuais")
            for row in cursor.fetchall():
                print(f"  - {row[0]} ({row[1]})")
            
            return True
        else:
            print("[ERRO] Tabela nao foi criada corretamente")
            return False
        
    except Exception as e:
        print(f"[ERRO] Falha na migracao: {e}")
        db.connection.rollback()
        return False
    finally:
        cursor.close()
        db.disconnect()

def main():
    """Função principal"""
    print("=" * 70)
    print("MIGRACAO: Adicionar tabela envios_individuais")
    print("=" * 70)
    print("\nEsta migracao criara uma nova tabela para armazenar")
    print("um hash unico para cada envio individual (fasciculo + destinatario)")
    
    if migrate():
        print("\n" + "=" * 70)
        print("[OK] MIGRACAO CONCLUIDA COM SUCESSO!")
        print("=" * 70)
        print("\nProximos passos:")
        print("  1. O sistema agora gerara hash unico para cada envio")
        print("  2. Cada destinatario tera seu proprio hash de rastreamento")
        print("  3. Use: SELECT * FROM envios_individuais; para ver os dados")
        return 0
    else:
        print("\n" + "=" * 70)
        print("[ERRO] MIGRACAO FALHOU!")
        print("=" * 70)
        print("\nVerifique:")
        print("  1. MySQL esta rodando")
        print("  2. Credenciais no .env estao corretas")
        print("  3. Usuario tem permissao para criar tabelas")
        return 1

if __name__ == "__main__":
    sys.exit(main())
