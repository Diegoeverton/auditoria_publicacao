# Guia de Início Rápido

## 1. Instalação

```bash
# Instale as dependências
pip install -r requirements.txt
```

## 2. Configuração

Copie o arquivo `.env.example` para `.env` e configure suas credenciais de email:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_ou_app_password
EMAIL_FROM=seu_email@gmail.com
```

### Configuração do Gmail

Se você usar Gmail, precisará:
1. Ativar a verificação em duas etapas
2. Gerar uma "Senha de app" em https://myaccount.google.com/apppasswords
3. Usar essa senha no campo `SMTP_PASSWORD`

## 3. Preparação

Coloque seus arquivos PDF na pasta `fasciculos/`:

```bash
mkdir fasciculos
# Copie seus PDFs para esta pasta
```

## 4. Fluxo de Trabalho Completo

### Passo 1: Gerar Hash para um Fascículo

```bash
python main.py --edicao "Edição 001" --fasciculo "Fascículo 01" --pdf "fasciculos/fasciculo01.pdf"
```

Isso irá:
- ✓ Gerar um hash único para o fascículo
- ✓ Criptografar as informações sensíveis
- ✓ Registrar tudo na blockchain
- ✓ Salvar o hash em `data/hash_<ID>.json`

**Saída esperada:**
```
======================================================================
SISTEMA DE GERAÇÃO DE HASH PARA FASCÍCULOS
======================================================================

Edição: Edição 001
Fascículo: Fascículo 01
PDF: fasciculos/fasciculo01.pdf

[1/5] Inicializando componentes...
[2/5] Gerando hash do fascículo...
  ✓ Hash ID: abc123-def456-...
  ✓ Hash do Fascículo: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08...
[3/5] Registrando geração na blockchain...
[4/5] Criptografando informações sensíveis...
[5/5] Registrando criptografia na blockchain...

✓ HASH GERADO E REGISTRADO COM SUCESSO!

Hash ID: abc123-def456-...
```

### Passo 2: Enviar Fascículo por Email

```bash
python send_system.py --hash-id abc123-def456-... --destinatario destinatario@exemplo.com
```

Você pode adicionar opções:
```bash
python send_system.py \
  --hash-id abc123-def456-... \
  --destinatario destinatario@exemplo.com \
  --assunto "Fascículo Especial - Edição 001" \
  --mensagem "Segue em anexo o fascículo solicitado."
```

Isso irá:
- ✓ Descriptografar as informações do fascículo
- ✓ Enviar o PDF por email
- ✓ Registrar o envio na blockchain

### Passo 3: Consultar Auditoria

#### Consultar por Hash ID específico:
```bash
python audit_query.py --hash-id abc123-def456-...
```

**Saída esperada:**
```
======================================================================
TRILHA DE AUDITORIA - Hash ID: abc123-def456-...
======================================================================

Edição: Edição 001
Fascículo: Fascículo 01
Total de eventos: 4

----------------------------------------------------------------------
EVENTOS NA TRILHA DE AUDITORIA
----------------------------------------------------------------------
+-------+---------------------+---------------------------+------------------+
| Bloco | Data/Hora           | Ação                      | Destinatário     |
+=======+=====================+===========================+==================+
| 1     | 12/01/2026 19:00:00 | HASH_GENERATED           | -                |
+-------+---------------------+---------------------------+------------------+
| 2     | 12/01/2026 19:00:01 | HASH_ENCRYPTED           | -                |
+-------+---------------------+---------------------------+------------------+
| 3     | 12/01/2026 19:05:00 | HASH_DECRYPTED           | dest@exemplo.com |
+-------+---------------------+---------------------------+------------------+
| 4     | 12/01/2026 19:05:02 | EMAIL_SENT               | dest@exemplo.com |
+-------+---------------------+---------------------------+------------------+
```

#### Consultar todos os fascículos de uma edição:
```bash
python audit_query.py --edicao "Edição 001"
```

#### Verificar integridade da blockchain:
```bash
python audit_query.py --verificar-integridade
```

#### Ver estatísticas gerais:
```bash
python audit_query.py --estatisticas
```

## 5. Exemplo Completo

```bash
# 1. Gerar hash para 3 fascículos
python main.py --edicao "Edição 001" --fasciculo "Fascículo 01" --pdf "fasciculos/f01.pdf"
python main.py --edicao "Edição 001" --fasciculo "Fascículo 02" --pdf "fasciculos/f02.pdf"
python main.py --edicao "Edição 001" --fasciculo "Fascículo 03" --pdf "fasciculos/f03.pdf"

# 2. Enviar para diferentes destinatários
python send_system.py --hash-id <hash-id-1> --destinatario pessoa1@exemplo.com
python send_system.py --hash-id <hash-id-2> --destinatario pessoa2@exemplo.com
python send_system.py --hash-id <hash-id-3> --destinatario pessoa3@exemplo.com

# 3. Consultar auditoria da edição
python audit_query.py --edicao "Edição 001"

# 4. Verificar integridade
python audit_query.py --verificar-integridade
```

## 6. Estrutura de Dados

### Arquivo de Hash (`data/hash_<ID>.json`)
```json
{
  "hash_id": "abc123-def456-...",
  "edicao": "Edição 001",
  "fasciculo": "Fascículo 01",
  "encrypted_data": "gAAAAABh...",
  "timestamp": "2026-01-12T19:00:00.000000",
  "algorithm": "sha256",
  "is_encrypted": true
}
```

### Blockchain (`data/blockchain.json`)
```json
[
  {
    "index": 0,
    "timestamp": "2026-01-12T19:00:00.000000",
    "data": { "message": "Bloco Gênesis" },
    "previous_hash": "0",
    "block_type": "GENESIS",
    "hash": "abc123..."
  },
  {
    "index": 1,
    "timestamp": "2026-01-12T19:00:01.000000",
    "data": {
      "hash_id": "abc123-def456-...",
      "edicao": "Edição 001",
      "fasciculo": "Fascículo 01",
      "action": "Hash gerado para fascículo"
    },
    "previous_hash": "abc123...",
    "block_type": "HASH_GENERATED",
    "hash": "def456..."
  }
]
```

## 7. Segurança

- **Hashes SHA-256**: Garantem integridade dos fascículos
- **Criptografia AES-256**: Protege informações sensíveis
- **Blockchain**: Garante imutabilidade dos registros
- **Chave de criptografia**: Armazenada em `data/keys/encryption.key` (mantenha segura!)

## 8. Troubleshooting

### Erro: "Arquivo PDF não encontrado"
- Verifique se o caminho do PDF está correto
- Use caminhos absolutos ou relativos à raiz do projeto

### Erro: "Configurações de email não definidas"
- Verifique se o arquivo `.env` existe
- Confirme que as credenciais SMTP estão corretas
- Para Gmail, use uma "Senha de app"

### Erro: "Arquivo de hash não encontrado"
- Certifique-se de executar `main.py` antes de `send_system.py`
- Verifique se o hash_id está correto

## 9. Backup

Faça backup regular de:
- `data/blockchain.json` - Toda a trilha de auditoria
- `data/keys/encryption.key` - Chave de criptografia (CRÍTICO!)
- `data/hash_*.json` - Arquivos de hash individuais

## 10. Próximos Passos

- Explore as estatísticas: `python audit_query.py --estatisticas`
- Verifique regularmente a integridade: `python audit_query.py --verificar-integridade`
- Mantenha backups da blockchain e das chaves
