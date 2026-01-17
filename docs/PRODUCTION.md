# 🚀 Guia de Produção - Sistema de Auditoria de Publicação

## ✅ Pré-requisitos

Antes de usar em produção, certifique-se de que:

- [x] Dependências instaladas (`pip install -r requirements.txt`)
- [x] Sistema testado (`python demo.py` executado com sucesso)
- [ ] Credenciais de email configuradas
- [ ] PDFs dos fascículos preparados
- [ ] Backup configurado

---

## 📧 Passo 1: Configurar Email (OBRIGATÓRIO)

### 1.1 Criar arquivo de configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env
```

### 1.2 Configurar credenciais

Edite o arquivo `.env` com suas credenciais:

```env
# Configurações de Email SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_ou_app_password
EMAIL_FROM=seu_email@gmail.com
```

### 1.3 Configuração por Provedor

#### 📧 Gmail (Recomendado)

1. **Ativar verificação em duas etapas**
   - Acesse: https://myaccount.google.com/security
   - Ative a "Verificação em duas etapas"

2. **Gerar Senha de App**
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App": Outro (nome personalizado)
   - Digite: "Sistema Auditoria"
   - Copie a senha gerada (16 caracteres)

3. **Configure no .env**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=seu_email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Senha de app gerada
   EMAIL_FROM=seu_email@gmail.com
   ```

#### 📧 Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu_email@outlook.com
SMTP_PASSWORD=sua_senha
EMAIL_FROM=seu_email@outlook.com
```

#### 📧 Yahoo

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=seu_email@yahoo.com
SMTP_PASSWORD=sua_senha_de_app
EMAIL_FROM=seu_email@yahoo.com
```

#### 📧 Servidor SMTP Customizado

```env
SMTP_SERVER=smtp.seuservidor.com
SMTP_PORT=587
SMTP_USER=seu_usuario
SMTP_PASSWORD=sua_senha
EMAIL_FROM=remetente@seudominio.com
```

### 1.4 Testar Configuração

```bash
# Teste a conexão SMTP
python -c "from src.email_sender import EmailSender; from src.config import SMTP_CONFIG; sender = EmailSender(SMTP_CONFIG); sender.test_connection()"
```

**Saída esperada:**
```
✓ Conexão SMTP bem-sucedida
```

---

## 📁 Passo 2: Preparar Fascículos

### 2.1 Organizar PDFs

Coloque seus arquivos PDF na pasta `fasciculos/`:

```bash
fasciculos/
├── edicao001_fasciculo01.pdf
├── edicao001_fasciculo02.pdf
├── edicao001_fasciculo03.pdf
└── ...
```

### 2.2 Verificar PDFs

Certifique-se de que:
- ✅ Arquivos são PDFs válidos
- ✅ Nomes são descritivos
- ✅ Tamanho é adequado para email (< 25 MB recomendado)

---

## 🔐 Passo 3: Uso em Produção

### 3.1 Fluxo Completo para UM Fascículo

```bash
# 1. Gerar hash para o fascículo
python main.py \
  --edicao "Edição 001" \
  --fasciculo "Fascículo 01" \
  --pdf "fasciculos/edicao001_fasciculo01.pdf"

# Anote o Hash ID retornado (exemplo: abc123-def456-...)

# 2. Enviar para destinatário
python send_system.py \
  --hash-id abc123-def456-... \
  --destinatario destinatario@exemplo.com

# 3. Consultar auditoria
python audit_query.py --hash-id abc123-def456-...
```

### 3.2 Fluxo para MÚLTIPLOS Fascículos

#### Opção A: Manual (Recomendado para poucos fascículos)

```bash
# Gerar hashes
python main.py --edicao "Ed001" --fasciculo "F01" --pdf "fasciculos/f01.pdf"
python main.py --edicao "Ed001" --fasciculo "F02" --pdf "fasciculos/f02.pdf"
python main.py --edicao "Ed001" --fasciculo "F03" --pdf "fasciculos/f03.pdf"

# Enviar (use os hash IDs gerados)
python send_system.py --hash-id <hash-id-1> --destinatario dest1@exemplo.com
python send_system.py --hash-id <hash-id-2> --destinatario dest2@exemplo.com
python send_system.py --hash-id <hash-id-3> --destinatario dest3@exemplo.com

# Consultar edição completa
python audit_query.py --edicao "Ed001"
```

#### Opção B: Script de Automação (Recomendado para muitos fascículos)

Crie um arquivo `enviar_edicao.py`:

```python
"""
Script de automação para enviar uma edição completa
"""
import subprocess
import json
import re

# Configuração
EDICAO = "Edição 001"
FASCICULOS = [
    {
        'nome': 'Fascículo 01',
        'pdf': 'fasciculos/edicao001_fasciculo01.pdf',
        'destinatarios': ['pessoa1@exemplo.com', 'pessoa2@exemplo.com']
    },
    {
        'nome': 'Fascículo 02',
        'pdf': 'fasciculos/edicao001_fasciculo02.pdf',
        'destinatarios': ['pessoa3@exemplo.com']
    },
    # Adicione mais fascículos aqui
]

def extrair_hash_id(output):
    """Extrai hash ID da saída do main.py"""
    match = re.search(r'Hash ID: ([a-f0-9-]+)', output)
    return match.group(1) if match else None

print("=" * 70)
print(f"PROCESSANDO EDIÇÃO: {EDICAO}")
print("=" * 70)

for i, fasciculo in enumerate(FASCICULOS, 1):
    print(f"\n[{i}/{len(FASCICULOS)}] Processando {fasciculo['nome']}...")
    
    # 1. Gerar hash
    print("  → Gerando hash...")
    result = subprocess.run(
        ['python', 'main.py', 
         '--edicao', EDICAO,
         '--fasciculo', fasciculo['nome'],
         '--pdf', fasciculo['pdf']],
        capture_output=True,
        text=True
    )
    
    hash_id = extrair_hash_id(result.stdout)
    if not hash_id:
        print(f"  ✗ Erro ao gerar hash para {fasciculo['nome']}")
        continue
    
    print(f"  ✓ Hash gerado: {hash_id[:16]}...")
    
    # 2. Enviar para destinatários
    for dest in fasciculo['destinatarios']:
        print(f"  → Enviando para {dest}...")
        result = subprocess.run(
            ['python', 'send_system.py',
             '--hash-id', hash_id,
             '--destinatario', dest],
            capture_output=True,
            text=True
        )
        
        if 'SUCESSO' in result.stdout:
            print(f"  ✓ Enviado para {dest}")
        else:
            print(f"  ✗ Erro ao enviar para {dest}")

print("\n" + "=" * 70)
print("PROCESSAMENTO CONCLUÍDO")
print("=" * 70)

# Consultar auditoria da edição
print(f"\nConsultando auditoria da {EDICAO}...")
subprocess.run(['python', 'audit_query.py', '--edicao', EDICAO])
```

Execute:
```bash
python enviar_edicao.py
```

---

## 📊 Passo 4: Monitoramento e Auditoria

### 4.1 Consultas Úteis

```bash
# Ver todos os fascículos de uma edição
python audit_query.py --edicao "Edição 001"

# Ver trilha completa de um fascículo
python audit_query.py --hash-id <hash-id>

# Verificar integridade da blockchain
python audit_query.py --verificar-integridade

# Ver estatísticas gerais
python audit_query.py --estatisticas
```

### 4.2 Verificação Diária Recomendada

```bash
# Crie um script verificacao_diaria.bat (Windows)
@echo off
echo Verificacao Diaria - %date% %time%
python audit_query.py --verificar-integridade
python audit_query.py --estatisticas
pause
```

Ou `verificacao_diaria.sh` (Linux/Mac):
```bash
#!/bin/bash
echo "Verificacao Diaria - $(date)"
python audit_query.py --verificar-integridade
python audit_query.py --estatisticas
```

---

## 💾 Passo 5: Backup (CRÍTICO!)

### 5.1 Arquivos Críticos para Backup

```
CRÍTICO (perda = sistema inutilizado):
├── data/keys/encryption.key    # Chave de criptografia

IMPORTANTE (perda = histórico perdido):
├── data/blockchain.json         # Toda a trilha de auditoria
└── data/hash_*.json            # Hashes individuais
```

### 5.2 Script de Backup Automático

Crie `backup.py`:

```python
"""
Script de backup automático
"""
import shutil
import os
from datetime import datetime
from pathlib import Path

# Configuração
BACKUP_DIR = Path("backups")
DATA_DIR = Path("data")

# Criar diretório de backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = BACKUP_DIR / timestamp
backup_path.mkdir(parents=True, exist_ok=True)

print(f"Criando backup em: {backup_path}")

# Backup da blockchain
if (DATA_DIR / "blockchain.json").exists():
    shutil.copy2(DATA_DIR / "blockchain.json", backup_path / "blockchain.json")
    print("✓ Blockchain copiada")

# Backup da chave de criptografia
key_file = DATA_DIR / "keys" / "encryption.key"
if key_file.exists():
    (backup_path / "keys").mkdir(exist_ok=True)
    shutil.copy2(key_file, backup_path / "keys" / "encryption.key")
    print("✓ Chave de criptografia copiada")

# Backup dos hashes
hash_files = list(DATA_DIR.glob("hash_*.json"))
for hash_file in hash_files:
    shutil.copy2(hash_file, backup_path / hash_file.name)
print(f"✓ {len(hash_files)} arquivos de hash copiados")

print(f"\n✓ Backup concluído: {backup_path}")
print(f"Total de arquivos: {len(list(backup_path.rglob('*')))}")

# Limpar backups antigos (manter últimos 30 dias)
import time
for old_backup in BACKUP_DIR.iterdir():
    if old_backup.is_dir():
        age_days = (time.time() - old_backup.stat().st_mtime) / 86400
        if age_days > 30:
            shutil.rmtree(old_backup)
            print(f"✓ Backup antigo removido: {old_backup.name}")
```

Execute regularmente:
```bash
python backup.py
```

### 5.3 Agendar Backup Automático

**Windows (Agendador de Tarefas):**
```powershell
# Criar tarefa que executa diariamente às 23h
$action = New-ScheduledTaskAction -Execute "python" -Argument "D:\antigratity\audotoria_publicacao\backup.py" -WorkingDirectory "D:\antigratity\audotoria_publicacao"
$trigger = New-ScheduledTaskTrigger -Daily -At 11pm
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "BackupAuditoriaPublicacao" -Description "Backup diário do sistema de auditoria"
```

**Linux/Mac (Cron):**
```bash
# Editar crontab
crontab -e

# Adicionar linha (executa diariamente às 23h)
0 23 * * * cd /path/to/audotoria_publicacao && python backup.py >> /var/log/backup_auditoria.log 2>&1
```

---

## 🔒 Passo 6: Segurança em Produção

### 6.1 Permissões de Arquivos

```bash
# Linux/Mac - Proteger arquivos sensíveis
chmod 600 .env
chmod 600 data/keys/encryption.key
chmod 700 data/keys/
```

### 6.2 Checklist de Segurança

- [ ] Arquivo `.env` não está no controle de versão (git)
- [ ] Chave de criptografia tem backup seguro
- [ ] Senhas de email são "senhas de app", não senha principal
- [ ] Backup está em local seguro (preferencialmente externo)
- [ ] Permissões de arquivo estão restritas
- [ ] Verificação de integridade é executada regularmente

---

## 📋 Passo 7: Checklist de Produção

### Antes de Começar
- [ ] Dependências instaladas
- [ ] Email configurado e testado
- [ ] PDFs preparados e organizados
- [ ] Backup configurado
- [ ] Sistema testado com `demo.py`

### Para Cada Edição
- [ ] PDFs verificados e prontos
- [ ] Lista de destinatários preparada
- [ ] Hashes gerados para todos os fascículos
- [ ] Emails enviados com sucesso
- [ ] Auditoria consultada e verificada
- [ ] Backup realizado

### Manutenção Regular
- [ ] Verificação de integridade (diária)
- [ ] Backup (diário)
- [ ] Limpeza de backups antigos (mensal)
- [ ] Revisão de logs (semanal)

---

## 🚨 Troubleshooting em Produção

### Problema: Email não está sendo enviado

**Soluções:**
1. Verifique credenciais no `.env`
2. Para Gmail, certifique-se de usar "Senha de app"
3. Teste conexão: `python -m src.email_sender`
4. Verifique firewall/antivírus

### Problema: "Blockchain comprometida"

**Soluções:**
1. Restaure do backup mais recente
2. Verifique se arquivo foi editado manualmente
3. Se necessário, recrie blockchain (perda de histórico)

### Problema: Erro ao descriptografar

**Soluções:**
1. Verifique se a chave de criptografia é a mesma
2. Restaure chave do backup
3. Dados criptografados com chave diferente não podem ser recuperados

---

## 📞 Suporte

Para mais informações, consulte:
- **Comandos**: `COMMANDS.md`
- **Técnico**: `TECHNICAL.md`
- **Início Rápido**: `QUICKSTART.md`

---

## ✅ Sistema Pronto para Produção!

Após seguir todos os passos acima, seu sistema estará pronto para uso em produção com:

✅ Email configurado e testado  
✅ Fascículos organizados  
✅ Backup automático  
✅ Monitoramento configurado  
✅ Segurança implementada  

**Boa sorte com suas publicações! 🚀**
