# Documentação Técnica

## Arquitetura do Sistema

### Visão Geral

O sistema é composto por 4 módulos principais que trabalham em conjunto para fornecer rastreabilidade end-to-end:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO DO SISTEMA                              │
└─────────────────────────────────────────────────────────────────┘

1. GERAÇÃO DE HASH
   ┌──────────────┐
   │  Fascículo   │
   │   (PDF)      │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │ Hash Generator   │  → Gera hash SHA-256 único
   │ + Metadados PDF  │  → Extrai informações do PDF
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │  Hash Único      │  hash_id + fasciculo_hash
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │  Blockchain      │  → Registra: HASH_GENERATED
   └──────────────────┘

2. CRIPTOGRAFIA
   ┌──────────────────┐
   │  Hash Único      │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Crypto Manager   │  → Criptografia AES-256 (Fernet)
   │ (AES-256)        │  → Protege dados sensíveis
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Hash Criptografado│
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │  Blockchain      │  → Registra: HASH_ENCRYPTED
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Salva em arquivo │  data/hash_<ID>.json
   └──────────────────┘

3. DESCRIPTOGRAFIA E ENVIO
   ┌──────────────────┐
   │ Carrega arquivo  │  data/hash_<ID>.json
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Crypto Manager   │  → Descriptografa dados
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │  Blockchain      │  → Registra: HASH_DECRYPTED
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │  Email Sender    │  → Envia PDF + informações
   │  (SMTP)          │  → Template HTML profissional
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │  Blockchain      │  → Registra: EMAIL_SENT
   └──────┬───────────┘  → Destinatário + timestamp
          │
          ▼
   ┌──────────────────┐
   │  Destinatário    │  📧 Recebe fascículo
   └──────────────────┘

4. AUDITORIA
   ┌──────────────────┐
   │  Blockchain      │  → Cadeia imutável de eventos
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  Consultas Disponíveis:              │
   │  • Por Hash ID (trilha completa)     │
   │  • Por Edição (todos os fascículos)  │
   │  • Verificação de integridade        │
   │  • Estatísticas gerais               │
   └──────────────────────────────────────┘
```

## Componentes Detalhados

### 1. Hash Generator (`hash_generator.py`)

**Responsabilidade:** Gerar hashes únicos e verificáveis para cada fascículo.

**Algoritmo:**
- Hash principal: SHA-256
- Entrada: `hash_id | edição | fascículo | conteúdo_pdf | timestamp`
- Saída: Hash hexadecimal de 64 caracteres

**Funcionalidades:**
- Extração de metadados do PDF (título, autor, número de páginas, etc.)
- Geração de hash do conteúdo textual do PDF
- Criação de ID único (UUID v4)
- Verificação de integridade (comparação de hashes)

**Estrutura de Dados:**
```python
{
    'hash_id': 'uuid-v4',
    'fasciculo_hash': 'sha256-hex',
    'edicao': 'string',
    'fasciculo': 'string',
    'pdf_path': 'path',
    'pdf_size': int,
    'pdf_metadata': {
        'title': 'string',
        'author': 'string',
        'num_pages': int,
        ...
    },
    'timestamp': 'ISO-8601',
    'algorithm': 'sha256',
    'metadata': {}  # metadados customizados
}
```

### 2. Crypto Manager (`crypto_manager.py`)

**Responsabilidade:** Criptografar e descriptografar informações sensíveis.

**Algoritmo:**
- Criptografia: Fernet (AES-256 em modo CBC)
- Chave: Gerada automaticamente e armazenada em `data/keys/encryption.key`
- Encoding: Base64 URL-safe

**Funcionalidades:**
- Geração e gerenciamento de chaves
- Criptografia de dicionários Python (via JSON)
- Descriptografia com validação
- Assinatura digital (HMAC-SHA256)

**Dados Criptografados:**
- `fasciculo_hash`: Hash do fascículo
- `pdf_path`: Caminho do arquivo PDF
- `pdf_metadata`: Metadados extraídos do PDF

**Dados em Claro:**
- `hash_id`: ID único do fascículo
- `edicao`: Nome/número da edição
- `fasciculo`: Nome/número do fascículo
- `timestamp`: Data/hora de criação
- `algorithm`: Algoritmo de hash usado

### 3. Blockchain Audit (`blockchain_audit.py`)

**Responsabilidade:** Manter cadeia imutável de registros de auditoria.

**Estrutura de Bloco:**
```python
{
    'index': int,           # Posição na cadeia
    'timestamp': 'ISO-8601',
    'data': {},            # Dados do evento
    'previous_hash': 'hex', # Hash do bloco anterior
    'block_type': 'enum',  # Tipo do evento
    'hash': 'hex'          # Hash deste bloco
}
```

**Tipos de Blocos:**
- `GENESIS`: Bloco inicial da blockchain
- `HASH_GENERATED`: Hash gerado para fascículo
- `HASH_ENCRYPTED`: Hash criptografado
- `HASH_DECRYPTED`: Hash descriptografado para envio
- `EMAIL_SENT`: Email enviado com fascículo
- `VERIFICATION`: Verificação de integridade

**Algoritmo de Hash do Bloco:**
```
block_hash = SHA256(
    index + timestamp + data + previous_hash + block_type
)
```

**Verificação de Integridade:**
1. Para cada bloco (exceto gênesis):
   - Recalcula o hash do bloco
   - Compara com o hash armazenado
   - Verifica se `previous_hash` corresponde ao hash do bloco anterior
2. Se qualquer verificação falhar, a blockchain está comprometida

**Funcionalidades de Consulta:**
- `get_blocks_by_hash_id()`: Todos os blocos de um fascículo
- `get_blocks_by_edicao()`: Todos os blocos de uma edição
- `get_blocks_by_type()`: Todos os blocos de um tipo
- `get_audit_trail()`: Trilha completa ordenada por timestamp
- `verify_integrity()`: Verifica integridade da cadeia
- `get_statistics()`: Estatísticas gerais

### 4. Email Sender (`email_sender.py`)

**Responsabilidade:** Enviar fascículos por email com template profissional.

**Protocolo:** SMTP com STARTTLS

**Funcionalidades:**
- Envio de email com anexo PDF
- Template HTML responsivo e profissional
- Informações de rastreabilidade no corpo do email
- Teste de conexão SMTP

**Template de Email:**
- Header com título destacado
- Informações do fascículo (edição, número, data)
- ID único para rastreabilidade
- Nota sobre auditoria blockchain
- Footer com informações do sistema

**Configuração SMTP:**
```python
{
    'server': 'smtp.gmail.com',
    'port': 587,
    'user': 'email@exemplo.com',
    'password': 'senha_ou_app_password',
    'from': 'email@exemplo.com'
}
```

## Fluxo de Dados

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
    "timestamp": "2026-01-12T19:00:00",
    "data": {
      "message": "Bloco Gênesis"
    },
    "previous_hash": "0",
    "block_type": "GENESIS",
    "hash": "abc123..."
  },
  {
    "index": 1,
    "timestamp": "2026-01-12T19:00:01",
    "data": {
      "hash_id": "abc123-def456-...",
      "edicao": "Edição 001",
      "fasciculo": "Fascículo 01",
      "fasciculo_hash": "9f86d081...",
      "action": "Hash gerado para fascículo"
    },
    "previous_hash": "abc123...",
    "block_type": "HASH_GENERATED",
    "hash": "def456..."
  }
]
```

## Segurança

### Camadas de Segurança

1. **Hash SHA-256**
   - Garante integridade do conteúdo do PDF
   - Detecta qualquer alteração no arquivo
   - Irreversível (one-way function)

2. **Criptografia AES-256 (Fernet)**
   - Protege dados sensíveis em repouso
   - Chave simétrica armazenada localmente
   - Autenticação de mensagem integrada (HMAC)

3. **Blockchain**
   - Imutabilidade dos registros
   - Detecção de adulteração
   - Trilha de auditoria completa

4. **Timestamp UTC**
   - Registro temporal preciso
   - Ordem cronológica garantida
   - Não repúdio

### Considerações de Segurança

**Proteção da Chave:**
- A chave de criptografia (`data/keys/encryption.key`) é CRÍTICA
- Deve ser mantida em local seguro
- Fazer backup regular
- Considerar uso de HSM ou KMS em produção

**Backup:**
- Blockchain: `data/blockchain.json`
- Chave: `data/keys/encryption.key`
- Hashes: `data/hash_*.json`

**Limitações:**
- Sistema usa criptografia simétrica (mesma chave para criptografar/descriptografar)
- Não implementa assinatura digital com chave pública/privada
- Blockchain é local (não distribuída)

## Performance

### Complexidade Computacional

- **Geração de Hash:** O(n) onde n = tamanho do PDF
- **Criptografia/Descriptografia:** O(m) onde m = tamanho dos dados
- **Adição de Bloco:** O(1)
- **Verificação de Integridade:** O(b) onde b = número de blocos
- **Consulta por Hash ID:** O(b)

### Otimizações

- Hash do conteúdo PDF é armazenado (não o texto completo)
- Apenas dados sensíveis são criptografados
- Blockchain é carregada uma vez e mantida em memória
- Arquivos JSON são salvos de forma incremental

## Extensibilidade

### Possíveis Melhorias

1. **Assinatura Digital**
   - Implementar RSA para assinatura/verificação
   - Chave pública/privada para não-repúdio

2. **Blockchain Distribuída**
   - Implementar consenso (Proof of Work/Stake)
   - Múltiplos nós para redundância

3. **API REST**
   - Expor funcionalidades via API
   - Integração com outros sistemas

4. **Interface Web**
   - Dashboard para visualização
   - Upload de PDFs via browser

5. **Notificações**
   - Webhooks para eventos
   - Notificações em tempo real

6. **Compressão**
   - Comprimir PDFs antes de enviar
   - Reduzir tamanho da blockchain

7. **Multi-destinatário**
   - Envio em lote
   - Agendamento de envios

## Troubleshooting

### Problemas Comuns

**1. Erro: "Arquivo PDF não encontrado"**
- Verificar caminho do arquivo
- Usar caminho absoluto ou relativo correto

**2. Erro: "Configurações de email não definidas"**
- Criar arquivo `.env` a partir de `.env.example`
- Configurar credenciais SMTP corretas
- Para Gmail, usar "Senha de app"

**3. Erro: "Blockchain comprometida"**
- Verificar se arquivo `blockchain.json` foi alterado manualmente
- Restaurar de backup se disponível
- Criar nova blockchain (perda de histórico)

**4. Erro: "Erro ao descriptografar"**
- Verificar se a chave de criptografia é a mesma usada para criptografar
- Restaurar chave de backup se disponível
- Dados criptografados com chave diferente não podem ser recuperados

**5. Performance lenta**
- PDFs muito grandes podem demorar para processar
- Considerar processar em background
- Implementar cache de hashes

## Testes

### Testes Manuais

```bash
# 1. Teste de geração de hash
python -m src.hash_generator

# 2. Teste de criptografia
python -m src.crypto_manager

# 3. Teste de blockchain
python -m src.blockchain_audit

# 4. Teste de email (requer configuração)
python -m src.email_sender

# 5. Demonstração completa
python demo.py

# 6. Exemplo de uso
python exemplo_uso.py
```

### Testes de Integridade

```bash
# Verificar integridade da blockchain
python audit_query.py --verificar-integridade

# Ver estatísticas
python audit_query.py --estatisticas
```

## Licença e Uso

Este sistema foi desenvolvido para fins de auditoria e rastreabilidade de publicações.

**Recomendações:**
- Use em ambiente de produção apenas após testes adequados
- Mantenha backups regulares da blockchain e chaves
- Configure alertas para falhas de integridade
- Revise logs regularmente
