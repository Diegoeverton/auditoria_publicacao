# 🗄️ Guia de Uso do Banco de Dados MySQL

## 📋 Visão Geral

O sistema agora armazena todos os logs e hashes no **MySQL**, além do arquivo JSON blockchain. Isso permite:

✅ Consultas SQL rápidas e eficientes  
✅ Relatórios personalizados  
✅ Integração com outras ferramentas  
✅ Backup e recuperação facilitados  
✅ Escalabilidade para milhões de registros  

---

## 🚀 Instalação e Configuração

### 1. Instalar MySQL

**Windows:**
- Download: https://dev.mysql.com/downloads/installer/
- Instale o MySQL Server 8.0+
- Anote a senha do root

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Configurar .env

Edite o arquivo `.env` e adicione:

```env
# Configurações do Banco de Dados MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=auditoria_publicacao
DB_USER=root
DB_PASSWORD=sua_senha_mysql
DB_CHARSET=utf8mb4
```

### 3. Instalar Dependência Python

```bash
pip install mysql-connector-python==8.2.0
```

Ou reinstale todas as dependências:
```bash
pip install -r requirements.txt
```

### 4. Inicializar Banco de Dados

```bash
python init_database.py
```

**Saída esperada:**
```
======================================================================
INICIALIZAÇÃO DO BANCO DE DADOS
======================================================================

[1/4] Verificando configurações...
  Host: localhost
  Porta: 3306
  Banco: auditoria_publicacao
  Usuário: root

[2/4] Criando banco de dados...
✓ Banco de dados 'auditoria_publicacao' criado/verificado

[3/4] Criando tabelas...
✓ Tabelas criadas/verificadas com sucesso

[4/4] Verificando estrutura...
  ✓ Tabelas criadas e funcionando
  Total de registros: 0 fascículos

======================================================================
✓ BANCO DE DADOS INICIALIZADO COM SUCESSO!
======================================================================
```

---

## 📊 Estrutura do Banco de Dados

### Tabela: `fasciculos`

Armazena informações principais de cada fascículo.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID auto-incremento |
| `hash_id` | VARCHAR(255) | ID único do fascículo (UUID) |
| `edicao` | VARCHAR(255) | Nome/número da edição |
| `fasciculo` | VARCHAR(255) | Nome/número do fascículo |
| `fasciculo_hash` | VARCHAR(255) | Hash SHA-256 do PDF |
| `pdf_path` | TEXT | Caminho do arquivo PDF |
| `pdf_size` | BIGINT | Tamanho do PDF em bytes |
| `algorithm` | VARCHAR(50) | Algoritmo de hash usado |
| `created_at` | TIMESTAMP | Data/hora de criação |

### Tabela: `logs_eventos`

Armazena todos os eventos/logs do sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID auto-incremento |
| `hash_id` | VARCHAR(255) | Referência ao fascículo |
| `evento_tipo` | ENUM | Tipo do evento |
| `destinatario` | VARCHAR(255) | Email do destinatário |
| `nome_destinatario` | VARCHAR(255) | Nome do destinatário |
| `dados_adicionais` | JSON | Dados extras em JSON |
| `created_at` | TIMESTAMP | Data/hora do evento |

**Tipos de eventos:**
- `HASH_GENERATED` - Hash gerado
- `HASH_ENCRYPTED` - Hash criptografado
- `HASH_DECRYPTED` - Hash descriptografado
- `EMAIL_SENT` - Email enviado
- `VERIFICATION` - Verificação/auditoria

### Tabela: `envios_massa`

Armazena informações de envios em massa.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID auto-incremento |
| `hash_id` | VARCHAR(255) | Referência ao fascículo |
| `total_destinatarios` | INT | Total de destinatários |
| `enviados` | INT | Quantidade enviada |
| `erros` | INT | Quantidade de erros |
| `tempo_total_minutos` | DECIMAL | Tempo total em minutos |
| `status` | ENUM | Status do envio |
| `created_at` | TIMESTAMP | Início do envio |
| `completed_at` | TIMESTAMP | Fim do envio |

---

## 🔍 Consultando o Banco de Dados

### Usando o Script de Consulta

```bash
# Consultar fascículo específico
python consultar_db.py --hash-id abc123-def456-...

# Consultar todos os fascículos de uma edição
python consultar_db.py --edicao "Edição 001"

# Ver estatísticas gerais
python consultar_db.py --estatisticas

# Listar últimos 20 fascículos criados
python consultar_db.py --ultimos 20
```

### Consultas SQL Diretas

Conecte ao MySQL:
```bash
mysql -u root -p auditoria_publicacao
```

**Exemplos de consultas:**

```sql
-- Todos os fascículos de uma edição
SELECT * FROM fasciculos WHERE edicao = 'Edição 001';

-- Histórico completo de um fascículo
SELECT * FROM logs_eventos WHERE hash_id = 'abc123-def456-...';

-- Total de emails enviados por edição
SELECT f.edicao, COUNT(l.id) as total_emails
FROM fasciculos f
LEFT JOIN logs_eventos l ON f.hash_id = l.hash_id
WHERE l.evento_tipo = 'EMAIL_SENT'
GROUP BY f.edicao;

-- Fascículos enviados hoje
SELECT f.*, l.destinatario
FROM fasciculos f
JOIN logs_eventos l ON f.hash_id = l.hash_id
WHERE l.evento_tipo = 'EMAIL_SENT'
AND DATE(l.created_at) = CURDATE();

-- Destinatários que receberam mais de um fascículo
SELECT destinatario, COUNT(*) as total
FROM logs_eventos
WHERE evento_tipo = 'EMAIL_SENT'
GROUP BY destinatario
HAVING total > 1;
```

---

## 📈 Relatórios Úteis

### Relatório de Envios por Dia

```sql
SELECT 
    DATE(created_at) as data,
    COUNT(*) as total_envios
FROM logs_eventos
WHERE evento_tipo = 'EMAIL_SENT'
GROUP BY DATE(created_at)
ORDER BY data DESC;
```

### Relatório de Performance

```sql
SELECT 
    f.edicao,
    COUNT(DISTINCT f.hash_id) as total_fasciculos,
    COUNT(l.id) as total_envios,
    COUNT(DISTINCT l.destinatario) as destinatarios_unicos
FROM fasciculos f
LEFT JOIN logs_eventos l ON f.hash_id = l.hash_id AND l.evento_tipo = 'EMAIL_SENT'
GROUP BY f.edicao;
```

### Fascículos Pendentes de Envio

```sql
SELECT f.*
FROM fasciculos f
LEFT JOIN logs_eventos l ON f.hash_id = l.hash_id AND l.evento_tipo = 'EMAIL_SENT'
WHERE l.id IS NULL;
```

---

## 🔄 Integração com o Sistema Existente

O sistema continua usando blockchain JSON **E** MySQL simultaneamente:

- **Blockchain JSON**: Imutabilidade e verificação de integridade
- **MySQL**: Consultas rápidas e relatórios

Você não precisa mudar nada no uso atual! O sistema salva automaticamente em ambos.

---

## 💾 Backup do Banco de Dados

### Backup Completo

```bash
# Backup
mysqldump -u root -p auditoria_publicacao > backup_auditoria.sql

# Restaurar
mysql -u root -p auditoria_publicacao < backup_auditoria.sql
```

### Backup Automático (Script)

Crie `backup_mysql.bat` (Windows):
```batch
@echo off
set DATA=%date:~-4%%date:~3,2%%date:~0,2%
mysqldump -u root -p auditoria_publicacao > backup_%DATA%.sql
echo Backup criado: backup_%DATA%.sql
```

Ou `backup_mysql.sh` (Linux/Mac):
```bash
#!/bin/bash
DATA=$(date +%Y%m%d)
mysqldump -u root -p auditoria_publicacao > backup_$DATA.sql
echo "Backup criado: backup_$DATA.sql"
```

---

## 🛠️ Troubleshooting

### "Erro ao conectar ao MySQL"

**Soluções:**
1. Verifique se MySQL está rodando:
   ```bash
   # Windows
   net start MySQL80
   
   # Linux
   sudo systemctl status mysql
   ```

2. Teste conexão manual:
   ```bash
   mysql -u root -p
   ```

3. Verifique credenciais no `.env`

### "Tabelas não existem"

Execute:
```bash
python init_database.py
```

### "Access denied for user"

Verifique senha no `.env` ou crie novo usuário:
```sql
CREATE USER 'auditoria'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON auditoria_publicacao.* TO 'auditoria'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📊 Vantagens do MySQL

✅ **Performance**: Consultas muito mais rápidas que JSON  
✅ **Escalabilidade**: Suporta milhões de registros  
✅ **Relatórios**: SQL permite análises complexas  
✅ **Integridade**: Chaves estrangeiras garantem consistência  
✅ **Backup**: Ferramentas robustas de backup/restore  
✅ **Integração**: Fácil integrar com outras ferramentas  

---

## 🎯 Próximos Passos

1. ✅ Inicialize o banco: `python init_database.py`
2. ✅ Use o sistema normalmente (main.py, send_system.py, etc.)
3. ✅ Consulte logs: `python consultar_db.py --estatisticas`
4. ✅ Crie relatórios personalizados com SQL

**O sistema agora tem dupla proteção: Blockchain + MySQL! 🚀**
