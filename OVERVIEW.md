# 📄 Sistema de Auditoria de Publicação de Fascículos

## 🎯 Visão Geral

Sistema completo de controle e auditoria para publicação de fascículos em PDF com rastreabilidade **end-to-end** usando conceitos de **blockchain**.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  📄 PDF → 🔐 Hash → 🔒 Criptografia → 📧 Email → ⛓️ Blockchain  │
│                                                                 │
│              RASTREABILIDADE COMPLETA GARANTIDA                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Características Principais

✅ **Geração de Hash Único** - SHA-256 para cada fascículo  
✅ **Criptografia AES-256** - Proteção de dados sensíveis  
✅ **Blockchain de Auditoria** - Cadeia imutável de eventos  
✅ **Envio Automatizado** - Email com template profissional  
✅ **Trilha Completa** - Rastreamento de origem ao destino  
✅ **Verificação de Integridade** - Detecção de adulteração  

## 🚀 Início Rápido

### 1️⃣ Instalação
```bash
pip install -r requirements.txt
```

### 2️⃣ Configuração
```bash
cp .env.example .env
# Edite .env com suas credenciais de email
```

### 3️⃣ Uso Básico

**Gerar hash para um fascículo:**
```bash
python main.py \
  --edicao "Edição 001" \
  --fasciculo "Fascículo 01" \
  --pdf "fasciculos/fasciculo01.pdf"
```

**Enviar por email:**
```bash
python send_system.py \
  --hash-id <hash-id-gerado> \
  --destinatario destinatario@exemplo.com
```

**Consultar auditoria:**
```bash
python audit_query.py --hash-id <hash-id>
python audit_query.py --edicao "Edição 001"
python audit_query.py --verificar-integridade
```

## 📊 Fluxo do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. GERAÇÃO                                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Fascículo.pdf  →  Hash Generator  →  Hash Único              │
│                                                                 │
│   ✓ Hash SHA-256 do conteúdo                                   │
│   ✓ ID único (UUID)                                            │
│   ✓ Metadados do PDF                                           │
│   ✓ Registro na blockchain                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2. CRIPTOGRAFIA                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Hash Único  →  Crypto Manager  →  Hash Criptografado         │
│                                                                 │
│   ✓ Criptografia AES-256 (Fernet)                              │
│   ✓ Proteção de dados sensíveis                                │
│   ✓ Registro na blockchain                                     │
│   ✓ Salvo em arquivo JSON                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3. ENVIO                                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Hash Criptografado  →  Descriptografia  →  Email Sender      │
│                                                                 │
│   ✓ Descriptografia segura                                     │
│   ✓ Envio via SMTP                                             │
│   ✓ Template HTML profissional                                 │
│   ✓ Registro completo na blockchain                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 4. AUDITORIA                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Blockchain  →  Consultas  →  Trilha Completa                 │
│                                                                 │
│   ✓ Histórico completo de eventos                              │
│   ✓ Verificação de integridade                                 │
│   ✓ Consultas por hash, edição, tipo                           │
│   ✓ Estatísticas detalhadas                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Estrutura do Projeto

```
audotoria_publicacao/
│
├── 📄 README.md              # Documentação principal
├── 📄 QUICKSTART.md          # Guia de início rápido
├── 📄 TECHNICAL.md           # Documentação técnica
├── 📄 OVERVIEW.md            # Este arquivo
│
├── 🐍 main.py                # Sistema de geração de hash
├── 🐍 send_system.py         # Sistema de envio
├── 🐍 audit_query.py         # Sistema de consulta
├── 🐍 demo.py                # Demonstração interativa
├── 🐍 exemplo_uso.py         # Exemplos de uso
│
├── 📦 src/                   # Módulos principais
│   ├── hash_generator.py    # Geração de hashes
│   ├── crypto_manager.py    # Criptografia
│   ├── blockchain_audit.py  # Blockchain
│   ├── email_sender.py      # Envio de emails
│   └── config.py            # Configurações
│
├── 💾 data/                  # Dados do sistema
│   ├── blockchain.json      # Cadeia de auditoria
│   ├── hash_*.json          # Hashes individuais
│   └── keys/                # Chaves de criptografia
│
├── 📁 fasciculos/            # PDFs dos fascículos
│
├── ⚙️ .env                   # Configurações (criar)
├── ⚙️ .env.example           # Exemplo de configuração
├── 📋 requirements.txt       # Dependências Python
└── 🚫 .gitignore            # Arquivos ignorados

```

## 🔐 Segurança

### Camadas de Proteção

1. **Hash SHA-256**
   - Integridade do conteúdo
   - Detecção de alterações
   - Irreversível

2. **Criptografia AES-256**
   - Proteção em repouso
   - Dados sensíveis protegidos
   - Autenticação integrada

3. **Blockchain**
   - Imutabilidade
   - Detecção de adulteração
   - Trilha completa

4. **Timestamp UTC**
   - Registro temporal
   - Ordem cronológica
   - Não repúdio

## 📈 Exemplo de Trilha de Auditoria

```
╔════════════════════════════════════════════════════════════════╗
║  TRILHA DE AUDITORIA - Hash ID: abc123-def456-...              ║
╚════════════════════════════════════════════════════════════════╝

Edição: Edição 001
Fascículo: Fascículo 01
Total de eventos: 4

┌───────┬─────────────────────┬─────────────────┬──────────────────┐
│ Bloco │ Data/Hora           │ Ação            │ Destinatário     │
├───────┼─────────────────────┼─────────────────┼──────────────────┤
│   1   │ 12/01/2026 19:00:00 │ HASH_GENERATED  │ -                │
│   2   │ 12/01/2026 19:00:01 │ HASH_ENCRYPTED  │ -                │
│   3   │ 12/01/2026 19:05:00 │ HASH_DECRYPTED  │ dest@exemplo.com │
│   4   │ 12/01/2026 19:05:02 │ EMAIL_SENT      │ dest@exemplo.com │
└───────┴─────────────────────┴─────────────────┴──────────────────┘

✓ Rastreabilidade completa de origem ao destino
```

## 🎓 Casos de Uso

### 1. Publicação de Jornal Oficial
- Controle de distribuição de edições
- Auditoria de quem recebeu cada fascículo
- Verificação de integridade

### 2. Documentos Legais
- Rastreamento de envio de documentos
- Prova de entrega
- Cadeia de custódia

### 3. Publicações Científicas
- Distribuição controlada de artigos
- Registro de acesso
- Proteção de propriedade intelectual

### 4. Boletins Internos
- Controle de distribuição
- Auditoria de acesso
- Conformidade regulatória

## 📚 Documentação

- **README.md** - Visão geral e instalação
- **QUICKSTART.md** - Guia passo a passo com exemplos
- **TECHNICAL.md** - Arquitetura e detalhes técnicos
- **OVERVIEW.md** - Este arquivo (resumo visual)

## 🧪 Testes e Demonstração

```bash
# Demonstração completa (sem necessidade de configuração)
python demo.py

# Exemplos de uso programático
python exemplo_uso.py

# Testes individuais dos módulos
python -m src.hash_generator
python -m src.crypto_manager
python -m src.blockchain_audit
```

## 🔧 Configuração de Email

### Gmail
1. Ativar verificação em duas etapas
2. Gerar "Senha de app" em https://myaccount.google.com/apppasswords
3. Usar no arquivo `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=senha_de_app_gerada
EMAIL_FROM=seu_email@gmail.com
```

### Outros Provedores
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **SMTP Customizado**: Configure conforme seu provedor

## 📊 Estatísticas do Sistema

```bash
python audit_query.py --estatisticas
```

```
╔════════════════════════════════════════════════════════════════╗
║  ESTATÍSTICAS DA BLOCKCHAIN                                    ║
╚════════════════════════════════════════════════════════════════╝

Total de blocos: 15
Total de edições: 3
Total de fascículos: 8
Total de emails enviados: 6

Blocos por tipo:
  GENESIS: 1
  HASH_GENERATED: 8
  HASH_ENCRYPTED: 8
  HASH_DECRYPTED: 6
  EMAIL_SENT: 6
```

## 🆘 Suporte

### Problemas Comuns

**❌ "Arquivo PDF não encontrado"**
→ Verifique o caminho do arquivo

**❌ "Configurações de email não definidas"**
→ Configure o arquivo `.env`

**❌ "Erro ao descriptografar"**
→ Verifique se a chave de criptografia está correta

**❌ "Blockchain comprometida"**
→ Restaure de backup ou crie nova blockchain

### Verificação de Integridade

```bash
python audit_query.py --verificar-integridade
```

```
✓ BLOCKCHAIN ÍNTEGRA
  Todos os blocos estão válidos e a cadeia está intacta
```

## 🎯 Próximos Passos

1. ✅ Instalar dependências: `pip install -r requirements.txt`
2. ✅ Configurar email: Editar `.env`
3. ✅ Testar sistema: `python demo.py`
4. ✅ Gerar primeiro hash: `python main.py --help`
5. ✅ Enviar primeiro email: `python send_system.py --help`
6. ✅ Consultar auditoria: `python audit_query.py --help`

## 📝 Licença

Sistema desenvolvido para fins de auditoria e rastreabilidade de publicações.

---

**Desenvolvido com ❤️ usando Python**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  🔐 SEGURO  •  ⛓️ RASTREÁVEL  •  📊 AUDITÁVEL  •  🚀 EFICIENTE  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
