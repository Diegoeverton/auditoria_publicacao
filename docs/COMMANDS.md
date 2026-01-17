# Comandos Úteis - Sistema de Auditoria de Publicação

## 🚀 Comandos Principais

### Geração de Hash

```bash
# Gerar hash para um fascículo
python main.py --edicao "Edição 001" --fasciculo "Fascículo 01" --pdf "fasciculos/fasciculo01.pdf"

# Com metadados adicionais
python main.py --edicao "Edição 001" --fasciculo "Fascículo 01" --pdf "fasciculos/fasciculo01.pdf" --metadata '{"autor": "João Silva", "categoria": "Oficial"}'
```

### Envio de Email

```bash
# Envio básico
python send_system.py --hash-id <hash-id> --destinatario destinatario@exemplo.com

# Envio com assunto e mensagem customizados
python send_system.py --hash-id <hash-id> --destinatario destinatario@exemplo.com --assunto "Fascículo Especial" --mensagem "Segue em anexo o documento solicitado."
```

### Consultas de Auditoria

```bash
# Consultar por hash ID específico
python audit_query.py --hash-id <hash-id>

# Consultar todos os fascículos de uma edição
python audit_query.py --edicao "Edição 001"

# Verificar integridade da blockchain
python audit_query.py --verificar-integridade

# Ver estatísticas gerais
python audit_query.py --estatisticas
```

## 🧪 Testes e Demonstração

```bash
# Demonstração interativa completa
python demo.py

# Exemplos de uso programático
python exemplo_uso.py

# Testar módulo de hash
python -m src.hash_generator

# Testar módulo de criptografia
python -m src.crypto_manager

# Testar módulo de blockchain
python -m src.blockchain_audit

# Testar módulo de email (requer configuração)
python -m src.email_sender
```

## 📦 Instalação e Configuração

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar arquivo de configuração
cp .env.example .env

# Editar configurações (use seu editor preferido)
notepad .env  # Windows
nano .env     # Linux/Mac
```

## 🔍 Verificação e Manutenção

```bash
# Verificar integridade da blockchain
python audit_query.py --verificar-integridade

# Ver estatísticas do sistema
python audit_query.py --estatisticas

# Listar arquivos de hash gerados
dir data\hash_*.json  # Windows
ls data/hash_*.json   # Linux/Mac

# Ver conteúdo da blockchain
type data\blockchain.json  # Windows
cat data/blockchain.json   # Linux/Mac
```

## 📊 Exemplos de Fluxo Completo

### Exemplo 1: Publicação de Edição Completa

```bash
# 1. Gerar hashes para todos os fascículos
python main.py --edicao "Edição 001" --fasciculo "Fascículo 01" --pdf "fasciculos/f01.pdf"
python main.py --edicao "Edição 001" --fasciculo "Fascículo 02" --pdf "fasciculos/f02.pdf"
python main.py --edicao "Edição 001" --fasciculo "Fascículo 03" --pdf "fasciculos/f03.pdf"

# 2. Enviar para destinatários
python send_system.py --hash-id <hash-id-1> --destinatario pessoa1@exemplo.com
python send_system.py --hash-id <hash-id-2> --destinatario pessoa2@exemplo.com
python send_system.py --hash-id <hash-id-3> --destinatario pessoa3@exemplo.com

# 3. Consultar auditoria da edição
python audit_query.py --edicao "Edição 001"

# 4. Verificar integridade
python audit_query.py --verificar-integridade
```

### Exemplo 2: Envio em Lote (Script PowerShell)

```powershell
# enviar_lote.ps1
$edicao = "Edição 001"
$destinatarios = @(
    "pessoa1@exemplo.com",
    "pessoa2@exemplo.com",
    "pessoa3@exemplo.com"
)

# Gerar hash
$output = python main.py --edicao $edicao --fasciculo "Fascículo 01" --pdf "fasciculos/f01.pdf"
$hashId = ($output | Select-String -Pattern "Hash ID: (.+)").Matches.Groups[1].Value

# Enviar para todos
foreach ($dest in $destinatarios) {
    Write-Host "Enviando para $dest..."
    python send_system.py --hash-id $hashId --destinatario $dest
}

Write-Host "Envio concluído!"
```

### Exemplo 3: Envio em Lote (Script Bash)

```bash
#!/bin/bash
# enviar_lote.sh

EDICAO="Edição 001"
DESTINATARIOS=(
    "pessoa1@exemplo.com"
    "pessoa2@exemplo.com"
    "pessoa3@exemplo.com"
)

# Gerar hash
OUTPUT=$(python main.py --edicao "$EDICAO" --fasciculo "Fascículo 01" --pdf "fasciculos/f01.pdf")
HASH_ID=$(echo "$OUTPUT" | grep "Hash ID:" | cut -d' ' -f3)

# Enviar para todos
for DEST in "${DESTINATARIOS[@]}"; do
    echo "Enviando para $DEST..."
    python send_system.py --hash-id "$HASH_ID" --destinatario "$DEST"
done

echo "Envio concluído!"
```

## 🔐 Backup e Restauração

### Backup

```bash
# Criar diretório de backup
mkdir backup

# Copiar arquivos críticos
cp data/blockchain.json backup/blockchain_$(date +%Y%m%d_%H%M%S).json
cp data/keys/encryption.key backup/encryption_key_$(date +%Y%m%d_%H%M%S).key
cp data/hash_*.json backup/

# Compactar backup (opcional)
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz backup/
```

### Restauração

```bash
# Restaurar blockchain
cp backup/blockchain_YYYYMMDD_HHMMSS.json data/blockchain.json

# Restaurar chave de criptografia
cp backup/encryption_key_YYYYMMDD_HHMMSS.key data/keys/encryption.key

# Verificar integridade após restauração
python audit_query.py --verificar-integridade
```

## 📈 Monitoramento

### Script de Monitoramento (PowerShell)

```powershell
# monitor.ps1
while ($true) {
    Clear-Host
    Write-Host "=== MONITORAMENTO DO SISTEMA ===" -ForegroundColor Green
    Write-Host ""
    
    # Estatísticas
    python audit_query.py --estatisticas
    
    Write-Host ""
    Write-Host "Última atualização: $(Get-Date)" -ForegroundColor Yellow
    Write-Host "Pressione Ctrl+C para sair"
    
    Start-Sleep -Seconds 30
}
```

### Script de Monitoramento (Bash)

```bash
#!/bin/bash
# monitor.sh

while true; do
    clear
    echo "=== MONITORAMENTO DO SISTEMA ==="
    echo ""
    
    # Estatísticas
    python audit_query.py --estatisticas
    
    echo ""
    echo "Última atualização: $(date)"
    echo "Pressione Ctrl+C para sair"
    
    sleep 30
done
```

## 🛠️ Troubleshooting

### Limpar Cache Python

```bash
# Windows
del /s /q __pycache__
del /s /q *.pyc

# Linux/Mac
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Recriar Blockchain (CUIDADO: Perde histórico!)

```bash
# Backup da blockchain atual
cp data/blockchain.json data/blockchain_backup.json

# Remover blockchain
rm data/blockchain.json

# Executar qualquer comando para recriar
python audit_query.py --estatisticas
```

### Regenerar Chave de Criptografia (CUIDADO: Dados criptografados anteriores não poderão ser descriptografados!)

```bash
# Backup da chave atual
cp data/keys/encryption.key data/keys/encryption_backup.key

# Remover chave
rm data/keys/encryption.key

# Executar qualquer comando para recriar
python -m src.crypto_manager
```

## 📝 Logs e Debug

### Habilitar Logs Detalhados

```python
# Adicione no início dos scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verificar Saída Detalhada

```bash
# Redirecionar saída para arquivo
python main.py --edicao "Teste" --fasciculo "Teste" --pdf "test.pdf" > output.log 2>&1

# Ver arquivo de log
cat output.log  # Linux/Mac
type output.log # Windows
```

## 🔄 Automação

### Tarefa Agendada (Windows)

```powershell
# Criar tarefa que executa diariamente às 9h
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\audit_query.py --verificar-integridade"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "VerificarIntegridadeBlockchain"
```

### Cron Job (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa diariamente às 9h)
0 9 * * * cd /path/to/audotoria_publicacao && python audit_query.py --verificar-integridade >> /var/log/blockchain_check.log 2>&1
```

## 📚 Referências Rápidas

### Ajuda dos Comandos

```bash
python main.py --help
python send_system.py --help
python audit_query.py --help
```

### Estrutura de Arquivos

```
data/
├── blockchain.json          # Blockchain completa
├── hash_<uuid>.json        # Hash individual de fascículo
└── keys/
    └── encryption.key      # Chave de criptografia (CRÍTICO!)
```

### Variáveis de Ambiente (.env)

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_ou_app_password
EMAIL_FROM=seu_email@gmail.com
```

## 🎯 Comandos Mais Usados

```bash
# Top 5 comandos mais usados

# 1. Gerar hash
python main.py --edicao "Ed001" --fasciculo "F01" --pdf "fasciculos/f01.pdf"

# 2. Enviar email
python send_system.py --hash-id <hash-id> --destinatario dest@exemplo.com

# 3. Consultar por edição
python audit_query.py --edicao "Ed001"

# 4. Verificar integridade
python audit_query.py --verificar-integridade

# 5. Ver estatísticas
python audit_query.py --estatisticas
```

---

**💡 Dica:** Salve este arquivo como referência rápida!

##### Comandos Úteis de Consulta 
# Ver estatísticas do banco
python consultar_db.py --estatisticas

# Ver últimos 10 fascículos
python consultar_db.py --ultimos 10

# Consultar fascículo específico
python consultar_db.py --hash-id <hash-id>

# Ver todos os fascículos de uma edição
python consultar_db.py --edicao "Edição 001"