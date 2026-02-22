"""
Email service for sending emails
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "PhishGuard AI")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text content
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            # Add HTML content
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str,
        frontend_url: str = "http://localhost:5173"
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: User's email address
            username: User's username
            reset_token: Password reset token
            frontend_url: Frontend application URL
        
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "Réinitialisation de votre mot de passe - PhishGuard AI"
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 16px;
                    padding: 40px;
                    color: white;
                }}
                .content {{
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    margin-top: 20px;
                    color: #333;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .warning {{
                    background: #fff5f5;
                    border-left: 4px solid #f56565;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                }}
                .token-box {{
                    background: #f7fafc;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                    font-family: monospace;
                    font-size: 16px;
                    text-align: center;
                    color: #2d3748;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🛡️ PhishGuard AI</div>
                <h1 style="margin: 0;">Réinitialisation de mot de passe</h1>
                
                <div class="content">
                    <p>Bonjour <strong>{username}</strong>,</p>
                    
                    <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte PhishGuard AI.</p>
                    
                    <p>Cliquez sur le bouton ci-dessous pour réinitialiser votre mot de passe :</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
                    </div>
                    
                    <p>Ou copiez et collez ce lien dans votre navigateur :</p>
                    <div class="token-box">{reset_link}</div>
                    
                    <div class="warning">
                        <strong>⚠️ Important :</strong>
                        <ul style="margin: 10px 0;">
                            <li>Ce lien est valide pendant <strong>1 heure</strong></li>
                            <li>Il ne peut être utilisé qu'<strong>une seule fois</strong></li>
                            <li>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email</li>
                        </ul>
                    </div>
                    
                    <p style="margin-top: 30px; color: #718096; font-size: 14px;">
                        Pour des raisons de sécurité, nous ne pouvons pas vous envoyer votre mot de passe actuel. 
                        Vous devez en créer un nouveau.
                    </p>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé par PhishGuard AI</p>
                    <p>Si vous avez des questions, contactez notre support</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text content
        text_content = f"""
        PhishGuard AI - Réinitialisation de mot de passe
        
        Bonjour {username},
        
        Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.
        
        Cliquez sur ce lien pour réinitialiser votre mot de passe :
        {reset_link}
        
        Ce lien est valide pendant 1 heure et ne peut être utilisé qu'une seule fois.
        
        Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
        
        Cordialement,
        L'équipe PhishGuard AI
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
