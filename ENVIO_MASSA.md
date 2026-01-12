# 📧 Guia de Envio em Massa

## 🎯 Objetivo

Enviar o **mesmo fascículo para 1000+ destinatários** de forma automatizada, com:
- ✅ Controle de taxa de envio (evita bloqueio SMTP)
- ✅ Registro individual de cada envio na blockchain
- ✅ Rastreabilidade completa
- ✅ Estatísticas detalhadas

---

## 🚀 Uso Rápido

### Passo 1: Gerar o hash do fascículo (uma vez)

```bash
python main.py --edicao "Diário Oficial Jan/2026" --fasciculo "Edição Completa" --pdf "fasciculos/diario_jan2026.pdf"
```

**Anote o Hash ID retornado!** (exemplo: `abc123-def456-...`)

### Passo 2: Preparar lista de destinatários

Crie um arquivo com os emails. Você pode usar 3 formatos:

#### Opção A: Arquivo TXT (mais simples)
```txt
destinatario1@exemplo.com
destinatario2@exemplo.com
destinatario3@exemplo.com
...
```

#### Opção B: Arquivo JSON (com nomes)
```json
[
  {"email": "joao@exemplo.com", "nome": "João Silva"},
  {"email": "maria@exemplo.com", "nome": "Maria Santos"},
  ...
]
```

#### Opção C: Arquivo CSV (planilha)
```csv
email,nome
joao@exemplo.com,João Silva
maria@exemplo.com,Maria Santos
...
```

### Passo 3: Executar envio em massa

```bash
python envio_massa.py --hash-id <hash-id> --destinatarios lista_emails.txt
```

**Pronto!** O sistema enviará automaticamente para todos os destinatários.

---

## ⚙️ Opções Avançadas

### Controlar velocidade de envio

```bash
# Enviar com intervalo de 2 segundos entre emails
python envio_massa.py --hash-id <hash-id> --destinatarios lista.txt --intervalo 2.0

# Enviar em lotes de 50 (pausa maior a cada 50 emails)
python envio_massa.py --hash-id <hash-id> --destinatarios lista.txt --lote 50

# Combinar ambos
python envio_massa.py --hash-id <hash-id> --destinatarios lista.txt --intervalo 1.5 --lote 100
```

### Por que controlar a velocidade?

Provedores de email (Gmail, Outlook, etc.) têm limites:
- **Gmail**: ~500 emails/dia, ~100/hora
- **Outlook**: ~300 emails/dia
- **Servidores corporativos**: Varia

**Recomendações:**
- Para Gmail: `--intervalo 2.0 --lote 50`
- Para Outlook: `--intervalo 3.0 --lote 30`
- Para servidor próprio: Consulte seu administrador

---

## 📊 Exemplo Completo

### Cenário: Enviar Diário Oficial para 1000 assinantes

```bash
# 1. Gerar hash do fascículo
python main.py \
  --edicao "Diário Oficial Janeiro 2026" \
  --fasciculo "Edição Completa" \
  --pdf "fasciculos/diario_oficial_jan2026.pdf"

# Resultado: Hash ID: abc123-def456-789...

# 2. Preparar lista (arquivo: assinantes.txt)
# Coloque 1000 emails, um por linha

# 3. Enviar em massa
python envio_massa.py \
  --hash-id abc123-def456-789 \
  --destinatarios assinantes.txt \
  --intervalo 2.0 \
  --lote 100

# Saída esperada:
# [1/1000] Enviando para: email1@exemplo.com... ✓
# [2/1000] Enviando para: email2@exemplo.com... ✓
# [3/1000] Enviando para: email3@exemplo.com... ✓
# ...
# [100/1000] Enviando para: email100@exemplo.com... ✓
# ⏸ Pausa de 10s após 100 envios...
# [101/1000] Enviando para: email101@exemplo.com... ✓
# ...
```

---

## 📈 Estatísticas e Auditoria

### Durante o envio

O script mostra progresso em tempo real:
```
[523/1000] Enviando para: email523@exemplo.com... ✓
```

### Ao final

```
======================================================================
ENVIO EM MASSA CONCLUÍDO
======================================================================

📊 Estatísticas:
  Total de destinatários: 1000
  ✓ Enviados com sucesso: 987
  ✗ Erros: 13
  Taxa de sucesso: 98.7%
  Tempo total: 45.2 minutos
  Média: 2.7s por email
```

### Consultar auditoria

```bash
# Ver todos os envios deste fascículo
python audit_query.py --hash-id abc123-def456-789

# Ver estatísticas gerais
python audit_query.py --estatisticas
```

---

## 🔍 Rastreabilidade Individual

Cada envio é registrado individualmente na blockchain:

```json
{
  "hash_id": "abc123-def456-789",
  "edicao": "Diário Oficial Janeiro 2026",
  "fasciculo": "Edição Completa",
  "destinatario": "joao@exemplo.com",
  "nome_destinatario": "João Silva",
  "numero_envio": 523,
  "total_envios": 1000,
  "action": "Email enviado (523/1000)"
}
```

**Benefício:** Você pode provar que cada pessoa específica recebeu o email!

---

## ⚠️ Limitações e Cuidados

### Limites de Email

| Provedor | Limite Diário | Limite por Hora | Recomendação |
|----------|---------------|-----------------|--------------|
| Gmail | ~500 emails | ~100 emails | `--intervalo 2.0 --lote 50` |
| Outlook | ~300 emails | ~50 emails | `--intervalo 3.0 --lote 30` |
| Yahoo | ~500 emails | ~100 emails | `--intervalo 2.0 --lote 50` |
| Servidor Próprio | Varia | Varia | Consulte administrador |

### Tamanho do PDF

- **Gmail**: Máximo 25 MB por email
- **Outlook**: Máximo 20 MB por email
- **Recomendado**: PDFs até 10 MB

Se seu PDF for maior, considere:
1. Comprimir o PDF
2. Enviar link para download ao invés do anexo
3. Dividir em partes menores

### Tempo Estimado

Para 1000 emails com intervalo de 2 segundos:
- **Tempo mínimo**: ~33 minutos (2000 segundos)
- **Tempo real**: ~45-60 minutos (incluindo pausas e processamento)

---

## 🛠️ Troubleshooting

### "Erro: Configurações de email não definidas"
→ Configure o arquivo `.env` com suas credenciais SMTP

### "Erro: Arquivo de hash não encontrado"
→ Execute `main.py` primeiro para gerar o hash

### "Muitos erros de envio"
→ Aumente o intervalo: `--intervalo 3.0`

### "Conta bloqueada por spam"
→ Reduza a taxa de envio ou use servidor SMTP dedicado

### "PDF muito grande"
→ Comprima o PDF ou envie sem anexo

---

## 💡 Dicas para 1000+ Emails

### 1. Teste Primeiro
```bash
# Crie uma lista pequena de teste (5-10 emails)
python envio_massa.py --hash-id <hash-id> --destinatarios teste.txt
```

### 2. Divida em Lotes por Dia
```bash
# Dia 1: Primeiros 500
python envio_massa.py --hash-id <hash-id> --destinatarios lista_parte1.txt

# Dia 2: Últimos 500
python envio_massa.py --hash-id <hash-id> --destinatarios lista_parte2.txt
```

### 3. Use Servidor SMTP Dedicado

Para volumes grandes, considere:
- **SendGrid** (100 emails/dia grátis, depois pago)
- **Mailgun** (5000 emails/mês grátis)
- **Amazon SES** (62.000 emails/mês grátis)
- **Servidor SMTP próprio**

### 4. Monitore em Tempo Real

Abra outro terminal e execute:
```bash
# Ver estatísticas em tempo real
python audit_query.py --estatisticas
```

---

## 📋 Checklist para Envio em Massa

Antes de enviar para 1000+ pessoas:

- [ ] Hash do fascículo gerado
- [ ] Lista de destinatários preparada e validada
- [ ] Email configurado e testado
- [ ] Teste realizado com 5-10 emails
- [ ] Intervalo adequado configurado
- [ ] PDF tem tamanho adequado (< 10 MB)
- [ ] Backup realizado
- [ ] Tempo estimado calculado
- [ ] Monitoramento preparado

---

## 🎯 Exemplo de Uso Real

```bash
# Cenário: Prefeitura enviando Diário Oficial para 1500 assinantes

# 1. Gerar hash
python main.py \
  --edicao "Diário Oficial 12/01/2026" \
  --fasciculo "Edição 001" \
  --pdf "fasciculos/diario_12_01_2026.pdf"

# 2. Preparar lista (assinantes.txt com 1500 emails)

# 3. Teste com 10 emails
python envio_massa.py \
  --hash-id abc123 \
  --destinatarios teste_10.txt

# 4. Se teste OK, enviar para todos
python envio_massa.py \
  --hash-id abc123 \
  --destinatarios assinantes.txt \
  --intervalo 2.0 \
  --lote 100

# Tempo estimado: ~60 minutos
# Resultado: 1487 enviados, 13 erros (98.7% sucesso)
```

---

## ✅ Pronto para Usar!

O sistema está preparado para enviar o mesmo fascículo para quantos destinatários você precisar, com:

✅ Automação completa  
✅ Controle de taxa  
✅ Rastreabilidade individual  
✅ Registro na blockchain  
✅ Estatísticas detalhadas  

**Comece com um teste pequeno e depois escale! 🚀**
