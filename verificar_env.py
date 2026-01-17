"""
Script de teste para verificar configurações do .env
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

print("=" * 70)
print("VERIFICAÇÃO DAS CONFIGURAÇÕES DO .ENV")
print("=" * 70)

print("\n📧 Configurações de Email:")
print(f"  SMTP_SERVER: {os.getenv('SMTP_SERVER', 'NÃO DEFINIDO')}")
print(f"  SMTP_PORT: {os.getenv('SMTP_PORT', 'NÃO DEFINIDO')}")
print(f"  SMTP_USER: {os.getenv('SMTP_USER', 'NÃO DEFINIDO')}")
print(f"  SMTP_PASSWORD: {'***' if os.getenv('SMTP_PASSWORD') else 'NÃO DEFINIDO'}")
print(f"  EMAIL_FROM: {os.getenv('EMAIL_FROM', 'NÃO DEFINIDO')}")

print("\n🗄️ Configurações do MySQL:")
print(f"  DB_HOST: {os.getenv('DB_HOST', 'NÃO DEFINIDO')}")
print(f"  DB_PORT: {os.getenv('DB_PORT', 'NÃO DEFINIDO')}")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'NÃO DEFINIDO')}")
print(f"  DB_USER: {os.getenv('DB_USER', 'NÃO DEFINIDO')}")
print(f"  DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'NÃO DEFINIDO'}")
print(f"  DB_CHARSET: {os.getenv('DB_CHARSET', 'NÃO DEFINIDO')}")

print("\n" + "=" * 70)

# Verificar problemas
problemas = []

if not os.getenv('DB_HOST'):
    problemas.append("DB_HOST não está definido")
if not os.getenv('DB_USER'):
    problemas.append("DB_USER não está definido")
if not os.getenv('DB_PASSWORD'):
    problemas.append("⚠ DB_PASSWORD não está definido (pode ser vazio se MySQL não tem senha)")

if problemas:
    print("\n⚠ PROBLEMAS ENCONTRADOS:")
    for p in problemas:
        print(f"  - {p}")
    print("\nEdite o arquivo .env e adicione as configurações faltantes.")
else:
    print("\n✓ Todas as configurações necessárias estão definidas!")
