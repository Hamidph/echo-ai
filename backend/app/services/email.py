"""
Email service for sending transactional emails.

This module handles sending verification emails, password resets,
and other transactional emails using SMTP.
"""

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

from backend.app.core.config import get_settings
from backend.app.core.security import create_access_token

settings = get_settings()


# Email templates
VERIFICATION_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .button { background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; }
        .footer { margin-top: 30px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to AI Visibility!</h1>
        <p>Hi {{ user_name }},</p>
        <p>Thank you for registering with AI Visibility. Please verify your email address by clicking the button below:</p>
        <p style="margin: 30px 0;">
            <a href="{{ verification_url }}" class="button">Verify Email Address</a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{{ verification_url }}</p>
        <p>This link will expire in 24 hours.</p>
        <div class="footer">
            <p>If you didn't create this account, you can safely ignore this email.</p>
            <p>&copy; 2024 AI Visibility. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

PASSWORD_RESET_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .button { background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; }
        .footer { margin-top: 30px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Password Reset Request</h1>
        <p>Hi {{ user_name }},</p>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        <p style="margin: 30px 0;">
            <a href="{{ reset_url }}" class="button">Reset Password</a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{{ reset_url }}</p>
        <p>This link will expire in 1 hour.</p>
        <div class="footer">
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
            <p>&copy; 2024 AI Visibility. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
) -> None:
    """
    Send an email using SMTP.

    Args:
        to_email: Recipient email address.
        subject: Email subject.
        html_content: HTML content of the email.

    Raises:
        aiosmtplib.SMTPException: If email sending fails.
    """
    if not settings.smtp_username or not settings.smtp_password:
        # In development, just log the email
        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Content: {html_content[:200]}...")
        return

    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = settings.from_email
    message["To"] = to_email
    message["Subject"] = subject

    # Add HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    # Send email
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=True,
    )


async def send_verification_email(user_email: str, user_name: str, user_id: str) -> None:
    """
    Send email verification link.

    Args:
        user_email: User's email address.
        user_name: User's display name.
        user_id: User's ID for token generation.
    """
    # Generate verification token (valid for 24 hours)
    from datetime import timedelta
    token = create_access_token(
        data={"user_id": user_id, "type": "email_verification"},
        expires_delta=timedelta(hours=24),
    )

    # Build verification URL
    verification_url = f"{settings.frontend_url}/verify-email?token={token}"

    # Render template
    template = Template(VERIFICATION_EMAIL_TEMPLATE)
    html_content = template.render(
        user_name=user_name or "there",
        verification_url=verification_url,
    )

    # Send email
    await send_email(
        to_email=user_email,
        subject="Verify your AI Visibility account",
        html_content=html_content,
    )


async def send_password_reset_email(user_email: str, user_name: str, user_id: str) -> None:
    """
    Send password reset link.

    Args:
        user_email: User's email address.
        user_name: User's display name.
        user_id: User's ID for token generation.
    """
    # Generate reset token (valid for 1 hour)
    from datetime import timedelta
    token = create_access_token(
        data={"user_id": user_id, "type": "password_reset"},
        expires_delta=timedelta(hours=1),
    )

    # Build reset URL
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    # Render template
    template = Template(PASSWORD_RESET_TEMPLATE)
    html_content = template.render(
        user_name=user_name or "there",
        reset_url=reset_url,
    )

    # Send email
    await send_email(
        to_email=user_email,
        subject="Reset your AI Visibility password",
        html_content=html_content,
    )


async def send_welcome_email(user_email: str, user_name: str) -> None:
    """
    Send welcome email after email verification.

    Args:
        user_email: User's email address.
        user_name: User's display name.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to AI Visibility!</h1>
            <p>Hi {user_name or "there"},</p>
            <p>Your email has been verified successfully. You're all set to start analyzing brand visibility across LLM providers!</p>
            <p><strong>What's next?</strong></p>
            <ul>
                <li>Run your first experiment to see how your brand appears in AI responses</li>
                <li>Compare visibility across OpenAI, Anthropic, and Perplexity</li>
                <li>Track metrics like Share of Voice and Consistency Scores</li>
            </ul>
            <p>Get started: <a href="{settings.frontend_url}/dashboard">{settings.frontend_url}/dashboard</a></p>
            <p>Questions? Reply to this email or visit our documentation.</p>
            <p>Best regards,<br>The AI Visibility Team</p>
        </div>
    </body>
    </html>
    """

    await send_email(
        to_email=user_email,
        subject="Welcome to AI Visibility!",
        html_content=html_content,
    )
