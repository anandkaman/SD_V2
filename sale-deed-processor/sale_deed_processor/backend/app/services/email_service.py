# backend/app/services/email_service.py

"""
Email Service Module

Handles sending email notifications for support tickets and other events.
Uses SMTP with Gmail for reliable email delivery.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(
        self,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_email: str = "formonexsolutions@gmail.com",
        smtp_password: str = None,  # SECURITY: Load from environment variable
        developer_email: str = "nitinkumar@formonex.in"
    ):
        """
        Initialize email service
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port (587 for TLS)
            smtp_email: Sender email address
            smtp_password: SMTP password (App Password for Gmail)
            developer_email: Developer email to receive notifications
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password or __import__('os').getenv("SMTP_PASSWORD", "")  # Load from env
        self.developer_email = developer_email
        self.sender_name = "Sale Deed AI System"
        
        if not self.smtp_password:
            logger.warning("SMTP password not configured. Email sending will fail.")
        
        logger.info(f"Email service initialized - Notifications will be sent to {developer_email}")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None
    ) -> bool:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            plain_body: Plain text fallback (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.smtp_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text version (fallback)
            if plain_body:
                part1 = MIMEText(plain_body, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_support_ticket_notification(self, ticket_data: Dict) -> bool:
        """
        Send notification email when new support ticket is created
        
        Args:
            ticket_data: Dictionary containing ticket information
                - ticket_id: Ticket ID
                - user_name: User who created ticket
                - error_type: Type of error
                - error_description: Detailed description
                - batch_id: Batch ID (optional)
                - created_at: Timestamp
                
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Extract ticket data
            ticket_id = ticket_data.get('ticket_id', 'N/A')
            user_name = ticket_data.get('user_name', 'Unknown User')
            error_type = ticket_data.get('error_type', 'General Error')
            error_description = ticket_data.get('error_description', 'No description provided')
            batch_id = ticket_data.get('batch_id', 'N/A')
            created_at = ticket_data.get('created_at', datetime.now())
            
            # Format timestamp
            if isinstance(created_at, str):
                timestamp = created_at
            else:
                timestamp = created_at.strftime('%d/%m/%Y, %I:%M:%S %p IST')
            
            # Email subject
            subject = f"🎫 New Support Ticket #{ticket_id} - {error_type}"
            
            # HTML email body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #613AF5 0%, #774BFF 100%);
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }}
        .ticket-info {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .info-row {{
            display: flex;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .info-row:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .label {{
            font-weight: bold;
            color: #613AF5;
            min-width: 150px;
        }}
        .value {{
            color: #333;
            flex: 1;
        }}
        .description {{
            background: #fff;
            padding: 15px;
            border-left: 4px solid #613AF5;
            margin: 20px 0;
            font-style: italic;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 0 0 8px 8px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-urgent {{
            background: #fee;
            color: #c00;
        }}
        .badge-normal {{
            background: #e3f2fd;
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎫 New Support Ticket</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Sale Deed AI - Support System</p>
    </div>
    
    <div class="content">
        <p>Hello Developer,</p>
        <p>A new support ticket has been created in the Sale Deed AI system. Please review and take appropriate action.</p>
        
        <div class="ticket-info">
            <div class="info-row">
                <span class="label">Ticket ID:</span>
                <span class="value"><strong>#{ticket_id}</strong></span>
            </div>
            <div class="info-row">
                <span class="label">User Name:</span>
                <span class="value">{user_name}</span>
            </div>
            <div class="info-row">
                <span class="label">Error Type:</span>
                <span class="value"><span class="badge badge-normal">{error_type}</span></span>
            </div>
            <div class="info-row">
                <span class="label">Batch ID:</span>
                <span class="value">{batch_id}</span>
            </div>
            <div class="info-row">
                <span class="label">Created At:</span>
                <span class="value">{timestamp}</span>
            </div>
        </div>
        
        <div class="description">
            <strong>Error Description:</strong><br>
            {error_description}
        </div>
        
        <p style="margin-top: 30px;">
            <strong>Next Steps:</strong>
        </p>
        <ol>
            <li>Log in to the Sale Deed AI Control Panel</li>
            <li>Navigate to Ticket Management</li>
            <li>Review ticket details and user information</li>
            <li>Investigate and resolve the issue</li>
            <li>Update ticket status to "Resolved"</li>
        </ol>
    </div>
    
    <div class="footer">
        <p>This is an automated notification from Sale Deed AI System</p>
        <p>© 2026 Formonex Solutions. All rights reserved.</p>
    </div>
</body>
</html>
            """
            
            # Plain text version (fallback)
            plain_body = f"""
NEW SUPPORT TICKET - Sale Deed AI

Ticket ID: #{ticket_id}
User Name: {user_name}
Error Type: {error_type}
Batch ID: {batch_id}
Created At: {timestamp}

Error Description:
{error_description}

Next Steps:
1. Log in to the Sale Deed AI Control Panel
2. Navigate to Ticket Management
3. Review ticket details and user information
4. Investigate and resolve the issue
5. Update ticket status to "Resolved"

---
This is an automated notification from Sale Deed AI System
© 2026 Formonex Solutions
            """
            
            # Send email
            success = self.send_email(
                to_email=self.developer_email,
                subject=subject,
                html_body=html_body,
                plain_body=plain_body
            )
            
            if success:
                logger.info(f"Support ticket notification sent for ticket #{ticket_id}")
            else:
                logger.error(f"Failed to send notification for ticket #{ticket_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending support ticket notification: {e}")
            return False


# Global email service instance
email_service = EmailService()
