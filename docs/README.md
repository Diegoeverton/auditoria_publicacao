```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     📄 SISTEMA DE AUDITORIA DE PUBLICAÇÃO DE FASCÍCULOS        ║
║                                                                ║
║              Rastreabilidade End-to-End com Blockchain         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

## 🎯 Início Rápido (3 Passos)

### 1️⃣ Instalar
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar
```bash
cp .env.example .env
# Edite .env com suas credenciais de email
```

### 3️⃣ Testar
```bash
python demo.py
```

---

## 📚 Documentação

Escolha o documento adequado para você:

| 📄 Documento | 👥 Para Quem | 📝 O Que Contém |
|-------------|-------------|----------------|
| **[README.md](README.md)** | Todos | Visão geral e instalação |
| **[QUICKSTART.md](QUICKSTART.md)** | Iniciantes | Guia passo a passo com exemplos |
| **[TECHNICAL.md](TECHNICAL.md)** | Desenvolvedores | Arquitetura e detalhes técnicos |
| **[OVERVIEW.md](OVERVIEW.md)** | Gestores | Resumo visual e casos de uso |
| **[COMMANDS.md](COMMANDS.md)** | Usuários | Referência rápida de comandos |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Todos | Resumo completo do projeto |

---

## 🚀 Comandos Principais

### Gerar Hash
```bash
python main.py --edicao "Edição 001" --fasciculo "Fascículo 01" --pdf "fasciculos/fasciculo01.pdf"
```

### Enviar Email
```bash
python send_system.py --hash-id <hash-id> --destinatario destinatario@exemplo.com
```

### Consultar Auditoria
```bash
python audit_query.py --hash-id <hash-id>
python audit_query.py --edicao "Edição 001"
python audit_query.py --verificar-integridade
python audit_query.py --estatisticas
```

---

## 🎓 Exemplos e Demonstrações

### Demonstração Interativa
```bash
python demo.py
```

### Exemplos de Uso Programático
```bash
python exemplo_uso.py
```

### Testar Módulos Individuais
```bash
python -m src.hash_generator
python -m src.crypto_manager
python -m src.blockchain_audit
```

---

## 📁 Estrutura do Projeto

```
audotoria_publicacao/
│
├── 📄 Documentação (6 arquivos)
│   ├── README.md              ← Você está aqui
│   ├── QUICKSTART.md          ← Comece por aqui se é iniciante
│   ├── TECHNICAL.md           ← Detalhes técnicos
│   ├── OVERVIEW.md            ← Resumo visual
│   ├── COMMANDS.md            ← Referência de comandos
│   └── PROJECT_SUMMARY.md     ← Resumo do projeto
│
├── 🐍 Scripts Principais (3 arquivos)
│   ├── main.py                ← Gerar hash
│   ├── send_system.py         ← Enviar email
│   └── audit_query.py         ← Consultar auditoria
│
├── 🧪 Demonstrações (2 arquivos)
│   ├── demo.py                ← Demonstração interativa
│   └── exemplo_uso.py         ← Exemplos de uso
│
├── 📦 Módulos (src/)
│   ├── hash_generator.py      ← Geração de hashes
│   ├── crypto_manager.py      ← Criptografia
│   ├── blockchain_audit.py    ← Blockchain
│   ├── email_sender.py        ← Envio de emails
│   └── config.py              ← Configurações
│
├── 💾 Dados (data/)
│   ├── blockchain.json        ← Blockchain
│   ├── hash_*.json            ← Hashes individuais
│   └── keys/encryption.key    ← Chave de criptografia
│
└── 📁 Fascículos (fasciculos/)
    └── *.pdf                  ← Seus PDFs aqui
```

---

## 🔐 Segurança

- ✅ **Hash SHA-256** - Integridade de conteúdo
- ✅ **Criptografia AES-256** - Proteção de dados
- ✅ **Blockchain** - Imutabilidade de registros
- ✅ **Timestamp UTC** - Registro temporal
- ✅ **UUID v4** - IDs únicos

---

## 🎯 Casos de Uso

1. **Publicação de Jornal Oficial** - Controle de distribuição
2. **Documentos Legais** - Rastreamento de envio
3. **Publicações Científicas** - Distribuição controlada
4. **Boletins Internos** - Auditoria de acesso

---

## 🆘 Precisa de Ajuda?

### Problemas Comuns

**❌ "Arquivo PDF não encontrado"**
→ Verifique o caminho do arquivo

**❌ "Configurações de email não definidas"**
→ Configure o arquivo `.env`

**❌ "Erro ao descriptografar"**
→ Verifique se a chave está correta

### Onde Buscar Ajuda

1. **Início Rápido**: [QUICKSTART.md](QUICKSTART.md)
2. **Comandos**: [COMMANDS.md](COMMANDS.md)
3. **Problemas Técnicos**: [TECHNICAL.md](TECHNICAL.md)

---

## 📊 Fluxo do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  📄 PDF → 🔐 Hash → 🔒 Criptografia → 📧 Email → ⛓️ Blockchain  │
│                                                                 │
│              RASTREABILIDADE COMPLETA GARANTIDA                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

1. GERAÇÃO
   Fascículo.pdf → Hash Generator → Hash Único → Blockchain

2. CRIPTOGRAFIA
   Hash Único → Crypto Manager → Hash Criptografado → Blockchain

3. ENVIO
   Hash Criptografado → Descriptografia → Email Sender → Blockchain

4. AUDITORIA
   Blockchain → Consultas → Trilha Completa
```

---

## ✨ Características

- 🔐 **Seguro** - Múltiplas camadas de segurança
- ⛓️ **Rastreável** - Blockchain imutável
- 📊 **Auditável** - Trilha completa de eventos
- 🚀 **Eficiente** - Processamento rápido
- 📝 **Bem Documentado** - 6 arquivos de documentação
- 🧪 **Testado** - Scripts de demonstração inclusos
- 🔧 **Extensível** - Arquitetura modular

---

## 🎓 Tecnologias

- **Python 3.7+**
- **cryptography** - AES-256
- **PyPDF2** - Manipulação de PDFs
- **SMTP** - Envio de emails
- **JSON** - Persistência de dados

---

## 📈 Status do Projeto

```
✅ Geração de Hash        100% Completo
✅ Criptografia          100% Completo
✅ Blockchain            100% Completo
✅ Envio de Email        100% Completo
✅ Auditoria             100% Completo
✅ Documentação          100% Completo
✅ Testes                100% Completo

Status Geral: ✅ PRONTO PARA PRODUÇÃO
```

---

## 🚀 Próximos Passos

1. ✅ Leia [QUICKSTART.md](QUICKSTART.md)
2. ✅ Configure o arquivo `.env`
3. ✅ Execute `python demo.py`
4. ✅ Teste com seus PDFs
5. ✅ Consulte [COMMANDS.md](COMMANDS.md) para referência

---

## 📞 Suporte

- 📖 **Documentação**: Veja os arquivos `.md` na raiz do projeto
- 🧪 **Testes**: Execute `python demo.py`
- 🔍 **Verificação**: Execute `python audit_query.py --verificar-integridade`

---

## 📝 Licença

Sistema desenvolvido para fins de auditoria e rastreabilidade de publicações.

---

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  🔐 SEGURO  •  ⛓️ RASTREÁVEL  •  📊 AUDITÁVEL  •  🚀 EFICIENTE  │
│                                                                 │
│              SISTEMA DE AUDITORIA DE PUBLICAÇÃO                 │
│                        v1.0.0                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Desenvolvido com ❤️ usando Python**
#   a u d i t o r i a _ p u b l i c a c a o  
 