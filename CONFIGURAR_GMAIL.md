# 📧 Guia de Configuração do Gmail para Envio de Emails

## 🎯 Objetivo

Configurar o Gmail para enviar emails através do sistema de auditoria de publicação.

---

## 📋 Passo a Passo Completo

### **Passo 1: Ativar Verificação em Duas Etapas**

1. Acesse: https://myaccount.google.com/security
2. Role até "Como fazer login no Google"
3. Clique em "Verificação em duas etapas"
4. Clique em "Começar"
5. Siga as instruções para ativar

⚠️ **Importante:** Sem verificação em duas etapas, você não pode criar senhas de app!

---

### **Passo 2: Gerar Senha de App**

1. Acesse: https://myaccount.google.com/apppasswords
2. Se pedir para fazer login novamente, faça
3. Em "Selecionar app", escolha: **"Outro (nome personalizado)"**
4. Digite: **"Sistema Auditoria Publicação"**
5. Clique em **"Gerar"**
6. **COPIE A SENHA DE 16 CARACTERES** que aparece
   - Formato: `xxxx xxxx xxxx xxxx`
   - ⚠️ Você só verá esta senha UMA VEZ!

---

### **Passo 3: Configurar o Arquivo .env**

Edite o arquivo `.env` e adicione:

```env
# Configurações de Email SMTP - Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_FROM=seu_email@gmail.com
```

**Substitua:**
- `seu_email@gmail.com` → Seu email do Gmail
- `xxxx xxxx xxxx xxxx` → A senha de app que você copiou

**Exemplo real:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=prefeitura.publicacoes@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=prefeitura.publicacoes@gmail.com
```

---

### **Passo 4: Testar Configuração**

Execute o script de teste:

```bash
python -c "from src.email_sender import EmailSender; from src.config import SMTP_CONFIG; sender = EmailSender(SMTP_CONFIG); sender.test_connection()"
```

**Saída esperada:**
```
✓ Conexão SMTP bem-sucedida
```

**Se der erro:**
- Verifique se a senha de app está correta
- Verifique se não tem espaços extras no .env
- Certifique-se de que verificação em duas etapas está ativa

---

## 🔒 Limites do Gmail

### Limites Diários

| Tipo de Conta | Limite Diário | Limite por Hora |
|---------------|---------------|-----------------|
| Gmail Gratuito | 500 emails | ~100 emails |
| Google Workspace | 2000 emails | ~200 emails |

### Recomendações

Para envios em massa, use:
```bash
# Intervalo de 2 segundos entre emails
python envio_massa.py --hash-id <hash-id> --destinatarios lista.txt --intervalo 2.0 --lote 50
```

Isso envia:
- 50 emails
- Pausa de 10 segundos
- Continua com próximos 50
- Total: ~30 emails/minuto

---

## ⚠️ Problemas Comuns

### "Senha incorreta"
- Você está usando a senha da sua conta (❌)
- Use a senha de app de 16 caracteres (✅)

### "Verificação em duas etapas necessária"
- Ative em: https://myaccount.google.com/security

### "Acesso bloqueado"
- Gmail pode bloquear se enviar muitos emails rápido
- Reduza a velocidade: `--intervalo 3.0`

### "Conta bloqueada por spam"
- Aguarde 24 horas
- Use intervalos maiores
- Considere Google Workspace para volumes maiores

---

## 🎯 Alternativas ao Gmail

Se precisar enviar mais de 500 emails/dia:

### **1. Google Workspace (Pago)**
- Limite: 2000 emails/dia
- Custo: ~R$ 30/mês por usuário
- Mais confiável para produção

### **2. SendGrid (Recomendado para produção)**
- Limite: 100 emails/dia GRÁTIS
- Depois: Planos a partir de $15/mês
- Configuração:
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=sua_api_key_do_sendgrid
```

### **3. Mailgun**
- Limite: 5000 emails/mês GRÁTIS
- Depois: Pay-as-you-go
- Configuração:
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@seu-dominio.mailgun.org
SMTP_PASSWORD=sua_senha_mailgun
```

### **4. Amazon SES**
- Limite: 62.000 emails/mês GRÁTIS
- Depois: $0.10 por 1000 emails
- Mais complexo de configurar

---

## ✅ Checklist de Configuração

- [ ] Verificação em duas etapas ativada
- [ ] Senha de app gerada
- [ ] Arquivo .env configurado
- [ ] Teste de conexão passou
- [ ] Primeiro email de teste enviado

---

## 📝 Exemplo de Teste Completo

```bash
# 1. Verificar configuração
python verificar_env.py

# 2. Testar conexão SMTP
python -m src.email_sender

# 3. Gerar hash de teste
python main.py --edicao "Teste" --fasciculo "Teste 01" --pdf "fasciculos/demo_fasciculo.pdf"

# 4. Enviar email de teste (use o hash-id gerado acima)
python send_system.py --hash-id <hash-id> --destinatario seu_email@gmail.com

# 5. Verificar se recebeu o email
```

---

## 🎓 Dicas de Segurança

1. **Nunca compartilhe** a senha de app
2. **Revogue senhas antigas** que não usa mais
3. **Use um email dedicado** para o sistema (ex: `publicacoes@empresa.com`)
4. **Monitore** a atividade da conta regularmente
5. **Ative alertas** de segurança do Google

---

## 📞 Suporte

Se tiver problemas:

1. Verifique: https://support.google.com/accounts/answer/185833
2. Execute: `python verificar_env.py`
3. Veja os logs: `logs/auditoria.log` (após implementar logging)

---

**Configuração do Gmail concluída! ✅**

Agora você pode enviar emails através do sistema de forma segura e confiável.
