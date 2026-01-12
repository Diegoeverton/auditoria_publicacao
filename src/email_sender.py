"""
Sistema de Envio de Email
Responsável por enviar fascículos por email
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class EmailSender:
    """Gerencia o envio de emails com fascículos"""
    
    def __init__(self, smtp_config: Dict[str, str]):
        """
        Inicializa o enviador de emails
        
        Args:
            smtp_config: Configurações SMTP (server, port, user, password, from)
        """
        self.smtp_config = smtp_config
    
    def send_fasciculo(
        self,
        destinatario: str,
        fasciculo_info: Dict,
        pdf_path: Path,
        assunto: Optional[str] = None,
        mensagem_adicional: Optional[str] = None
    ) -> Dict:
        """
        Envia um fascículo por email
        
        Args:
            destinatario: Email do destinatário
            fasciculo_info: Informações do fascículo (edicao, fasciculo, hash_id, etc)
            pdf_path: Caminho para o arquivo PDF
            assunto: Assunto do email (opcional)
            mensagem_adicional: Mensagem adicional no corpo do email (opcional)
        
        Returns:
            Dicionário com resultado do envio
        """
        try:
            # Cria mensagem
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from']
            msg['To'] = destinatario
            msg['Subject'] = assunto or f"Fascículo: {fasciculo_info['edicao']} - {fasciculo_info['fasciculo']}"
            
            # Corpo do email
            corpo = self._create_email_body(fasciculo_info, mensagem_adicional)
            msg.attach(MIMEText(corpo, 'html', 'utf-8'))
            
            # Anexa PDF se existir
            if pdf_path and pdf_path.exists():
                with open(pdf_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=pdf_path.name
                    )
                    msg.attach(pdf_attachment)
            
            # Envia email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['user'], self.smtp_config['password'])
                server.send_message(msg)
            
            return {
                'success': True,
                'destinatario': destinatario,
                'timestamp': datetime.utcnow().isoformat(),
                'hash_id': fasciculo_info.get('hash_id'),
                'edicao': fasciculo_info.get('edicao'),
                'fasciculo': fasciculo_info.get('fasciculo'),
                'message': 'Email enviado com sucesso'
            }
            
        except Exception as e:
            return {
                'success': False,
                'destinatario': destinatario,
                'timestamp': datetime.utcnow().isoformat(),
                'hash_id': fasciculo_info.get('hash_id'),
                'error': str(e),
                'message': f'Erro ao enviar email: {e}'
            }
    
    def _create_email_body(
        self,
        fasciculo_info: Dict,
        mensagem_adicional: Optional[str] = None
    ) -> str:
        """
        Cria o corpo HTML do email
        
        Args:
            fasciculo_info: Informações do fascículo
            mensagem_adicional: Mensagem adicional (opcional)
        
        Returns:
            HTML do corpo do email
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .info-box {{
                    background-color: #e8f5e9;
                    border-left: 4px solid #4CAF50;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .hash {{
                    font-family: monospace;
                    background-color: #f0f0f0;
                    padding: 5px;
                    border-radius: 3px;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Fascículo Recebido</h1>
                </div>
                <div class="content">
                    <h2>Informações do Fascículo</h2>
                    
                    <div class="info-box">
                        <p><strong>Edição:</strong> {fasciculo_info.get('edicao', 'N/A')}</p>
                        <p><strong>Fascículo:</strong> {fasciculo_info.get('fasciculo', 'N/A')}</p>
                        <p><strong>Data de Envio:</strong> {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} UTC</p>
                    </div>
                    
                    {f'<p>{mensagem_adicional}</p>' if mensagem_adicional else ''}
                    
                    <h3>Identificação Única</h3>
                    <p>Este fascículo possui um identificador único para rastreabilidade:</p>
                    <p class="hash"><strong>ID:</strong> {fasciculo_info.get('hash_id', 'N/A')}</p>
                    
                    <p style="margin-top: 20px;">
                        <strong>Nota:</strong> Este documento está registrado em um sistema de auditoria 
                        blockchain que garante a rastreabilidade e integridade da distribuição.
                    </p>
                </div>
                <div class="footer">
                    <p>Sistema de Auditoria de Publicação</p>
                    <p>Este é um email automático, por favor não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def test_connection(self) -> bool:
        """
        Testa a conexão SMTP
        
        Returns:
            True se a conexão foi bem-sucedida, False caso contrário
        """
        try:
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['user'], self.smtp_config['password'])
            print("✓ Conexão SMTP bem-sucedida")
            return True
        except Exception as e:
            print(f"✗ Erro na conexão SMTP: {e}")
            return False


if __name__ == "__main__":
    # Teste do enviador de email
    from config import SMTP_CONFIG
    
    print("=== Sistema de Envio de Email ===")
    
    # Verifica se as configurações estão definidas
    if not SMTP_CONFIG['user'] or not SMTP_CONFIG['password']:
        print("\n⚠ Configure as credenciais SMTP no arquivo .env para testar o envio de emails")
        print("Exemplo de configuração necessária:")
        print("  SMTP_USER=seu_email@gmail.com")
        print("  SMTP_PASSWORD=sua_senha_ou_app_password")
    else:
        sender = EmailSender(SMTP_CONFIG)
        
        # Testa conexão
        print("\nTestando conexão SMTP...")
        sender.test_connection()
