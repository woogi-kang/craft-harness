---
name: email
description: |
  이메일 발송, 템플릿 관리, SMTP/SendGrid/Resend 연동을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Email Skill

이메일 발송, 템플릿 관리, SMTP/SendGrid/Resend 연동을 구현합니다.

## Triggers

- "이메일", "email", "smtp", "sendgrid", "resend", "메일 발송"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `emailProvider` | ❌ | smtp/sendgrid/resend (기본: smtp) |

---

## Output

### Email Service Interface

```python
# app/domain/services/email.py
from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel, ConfigDict, Field


class EmailAttachment(BaseModel):
    """Email attachment data."""

    model_config = ConfigDict(frozen=True)

    filename: str
    content: bytes
    content_type: str


class EmailMessage(BaseModel):
    """Email message data.

    Uses Pydantic BaseModel for:
    - Built-in validation
    - Easy serialization
    - Consistent pattern with domain entities
    """

    model_config = ConfigDict(frozen=True)

    to: list[str]
    subject: str
    body_html: str
    body_text: str | None = None
    from_email: str | None = None
    from_name: str | None = None
    reply_to: str | None = None
    cc: list[str] | None = None
    bcc: list[str] | None = None
    attachments: list[EmailAttachment] | None = None


class EmailResult(BaseModel):
    """Email send result."""

    model_config = ConfigDict(frozen=True)

    success: bool
    message_id: str | None = None
    error: str | None = None

    @classmethod
    def ok(cls, message_id: str | None = None) -> Self:
        """Create successful result."""
        return cls(success=True, message_id=message_id)

    @classmethod
    def fail(cls, error: str) -> Self:
        """Create failed result."""
        return cls(success=False, error=error)


class EmailService(ABC):
    """Abstract email service interface."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send an email."""
        ...

    @abstractmethod
    async def send_template(
        self,
        to: list[str],
        template_id: str,
        template_data: dict,
        subject: str | None = None,
    ) -> EmailResult:
        """Send an email using a template."""
        ...
```

### SMTP Implementation

```python
# app/infrastructure/email/smtp.py
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib

from app.core.config import settings
from app.domain.services.email import (
    EmailService,
    EmailMessage,
    EmailResult,
)

import structlog

logger = structlog.get_logger()


class SMTPEmailService(EmailService):
    """SMTP email service implementation."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
    ) -> None:
        self._host = host or settings.SMTP_HOST
        self._port = port or settings.SMTP_PORT
        self._username = username or settings.SMTP_USERNAME
        self._password = password or settings.SMTP_PASSWORD
        self._use_tls = use_tls
        self._default_from = settings.EMAIL_FROM

    async def send(self, message: EmailMessage) -> EmailResult:
        """Send an email via SMTP."""
        try:
            msg = self._build_message(message)

            await aiosmtplib.send(
                msg,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                use_tls=self._use_tls,
            )

            await logger.ainfo(
                "Email sent via SMTP",
                to=message.to,
                subject=message.subject,
            )

            return EmailResult(success=True, message_id=msg["Message-ID"])

        except Exception as e:
            await logger.aerror(
                "Failed to send email via SMTP",
                to=message.to,
                error=str(e),
            )
            return EmailResult(success=False, error=str(e))

    async def send_template(
        self,
        to: list[str],
        template_id: str,
        template_data: dict,
        subject: str | None = None,
    ) -> EmailResult:
        """Send a templated email."""
        # Load and render template
        html_content = await self._render_template(template_id, template_data)
        text_content = await self._render_template(
            f"{template_id}_text", template_data, fallback=""
        )

        message = EmailMessage(
            to=to,
            subject=subject or template_data.get("subject", "No Subject"),
            body_html=html_content,
            body_text=text_content or None,
        )

        return await self.send(message)

    def _build_message(self, message: EmailMessage) -> MIMEMultipart:
        """Build MIME message."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = f"{message.from_name or 'System'} <{message.from_email or self._default_from}>"
        msg["To"] = ", ".join(message.to)

        if message.reply_to:
            msg["Reply-To"] = message.reply_to
        if message.cc:
            msg["Cc"] = ", ".join(message.cc)

        # Add text body
        if message.body_text:
            msg.attach(MIMEText(message.body_text, "plain", "utf-8"))

        # Add HTML body
        msg.attach(MIMEText(message.body_html, "html", "utf-8"))

        # Add attachments
        if message.attachments:
            for attachment in message.attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment.filename}",
                )
                msg.attach(part)

        return msg

    async def _render_template(
        self,
        template_id: str,
        data: dict,
        fallback: str | None = None,
    ) -> str:
        """Render email template."""
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        env = Environment(
            loader=FileSystemLoader("app/templates/email"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        try:
            template = env.get_template(f"{template_id}.html")
            return template.render(**data)
        except Exception:
            if fallback is not None:
                return fallback
            raise
```

### Resend Implementation

```python
# app/infrastructure/email/resend_service.py
import resend

from app.core.config import settings
from app.domain.services.email import (
    EmailService,
    EmailMessage,
    EmailResult,
)

import structlog

logger = structlog.get_logger()


class ResendEmailService(EmailService):
    """Resend email service implementation."""

    def __init__(self, api_key: str | None = None) -> None:
        resend.api_key = api_key or settings.RESEND_API_KEY
        self._default_from = settings.EMAIL_FROM

    async def send(self, message: EmailMessage) -> EmailResult:
        """Send an email via Resend."""
        try:
            params = {
                "from": f"{message.from_name or 'System'} <{message.from_email or self._default_from}>",
                "to": message.to,
                "subject": message.subject,
                "html": message.body_html,
            }

            if message.body_text:
                params["text"] = message.body_text
            if message.reply_to:
                params["reply_to"] = message.reply_to
            if message.cc:
                params["cc"] = message.cc
            if message.bcc:
                params["bcc"] = message.bcc

            # Resend SDK is sync, run in thread pool
            import asyncio

            result = await asyncio.to_thread(resend.Emails.send, params)

            await logger.ainfo(
                "Email sent via Resend",
                to=message.to,
                message_id=result.get("id"),
            )

            return EmailResult(
                success=True,
                message_id=result.get("id"),
            )

        except Exception as e:
            await logger.aerror(
                "Failed to send email via Resend",
                to=message.to,
                error=str(e),
            )
            return EmailResult(success=False, error=str(e))

    async def send_template(
        self,
        to: list[str],
        template_id: str,
        template_data: dict,
        subject: str | None = None,
    ) -> EmailResult:
        """Send a templated email using Resend's React Email."""
        # For Resend, templates are typically React Email components
        # This example uses a simple HTML template approach
        html_content = await self._render_template(template_id, template_data)

        message = EmailMessage(
            to=to,
            subject=subject or template_data.get("subject", "No Subject"),
            body_html=html_content,
        )

        return await self.send(message)

    async def _render_template(self, template_id: str, data: dict) -> str:
        """Render email template."""
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        env = Environment(
            loader=FileSystemLoader("app/templates/email"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        template = env.get_template(f"{template_id}.html")
        return template.render(**data)
```

### SendGrid Implementation

```python
# app/infrastructure/email/sendgrid_service.py
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
)
import base64

from app.core.config import settings
from app.domain.services.email import (
    EmailService,
    EmailMessage,
    EmailResult,
)

import structlog

logger = structlog.get_logger()


class SendGridEmailService(EmailService):
    """SendGrid email service implementation."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.SENDGRID_API_KEY
        self._client = SendGridAPIClient(self._api_key)
        self._default_from = settings.EMAIL_FROM

    async def send(self, message: EmailMessage) -> EmailResult:
        """Send an email via SendGrid."""
        try:
            mail = Mail(
                from_email=f"{message.from_name or 'System'} <{message.from_email or self._default_from}>",
                to_emails=message.to,
                subject=message.subject,
                html_content=message.body_html,
            )

            # Add plain text version if provided
            if message.body_text:
                mail.plain_text_content = message.body_text

            # Add CC recipients
            if message.cc:
                for cc_email in message.cc:
                    mail.add_cc(cc_email)

            # Add BCC recipients
            if message.bcc:
                for bcc_email in message.bcc:
                    mail.add_bcc(bcc_email)

            # Add reply-to
            if message.reply_to:
                mail.reply_to = message.reply_to

            # Add attachments
            if message.attachments:
                for attachment in message.attachments:
                    encoded_content = base64.b64encode(attachment.content).decode()
                    mail.add_attachment(
                        Attachment(
                            FileContent(encoded_content),
                            FileName(attachment.filename),
                            FileType(attachment.content_type),
                            Disposition("attachment"),
                        )
                    )

            # SendGrid SDK is sync, run in thread pool
            response = await asyncio.to_thread(self._client.send, mail)

            await logger.ainfo(
                "Email sent via SendGrid",
                to=message.to,
                status_code=response.status_code,
            )

            # Extract message ID from headers
            message_id = response.headers.get("X-Message-Id")

            return EmailResult(
                success=True,
                message_id=message_id,
            )

        except Exception as e:
            await logger.aerror(
                "Failed to send email via SendGrid",
                to=message.to,
                error=str(e),
            )
            return EmailResult(success=False, error=str(e))

    async def send_template(
        self,
        to: list[str],
        template_id: str,
        template_data: dict,
        subject: str | None = None,
    ) -> EmailResult:
        """Send a templated email using SendGrid dynamic templates.

        For SendGrid, you can use dynamic templates created in the SendGrid dashboard.
        The template_id should be the SendGrid template ID (e.g., 'd-xxxxxxxxxxxx').
        """
        try:
            mail = Mail(
                from_email=self._default_from,
                to_emails=to,
            )

            # Use SendGrid dynamic template
            if template_id.startswith("d-"):
                # It's a SendGrid dynamic template ID
                mail.template_id = template_id
                mail.dynamic_template_data = template_data
            else:
                # Fall back to local Jinja2 templates
                html_content = await self._render_template(template_id, template_data)
                mail.subject = subject or template_data.get("subject", "No Subject")
                mail.html_content = html_content

            response = await asyncio.to_thread(self._client.send, mail)

            return EmailResult(
                success=True,
                message_id=response.headers.get("X-Message-Id"),
            )

        except Exception as e:
            await logger.aerror(
                "Failed to send template email via SendGrid",
                to=to,
                template_id=template_id,
                error=str(e),
            )
            return EmailResult(success=False, error=str(e))

    async def _render_template(self, template_id: str, data: dict) -> str:
        """Render local Jinja2 email template."""
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        env = Environment(
            loader=FileSystemLoader("app/templates/email"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        template = env.get_template(f"{template_id}.html")
        return template.render(**data)
```

### Email Application Service

```python
# app/application/services/email.py
from typing import Any

from app.domain.services.email import EmailService, EmailMessage, EmailResult

import structlog

logger = structlog.get_logger()


class EmailApplicationService:
    """Application service for email operations."""

    def __init__(self, email_service: EmailService) -> None:
        self._email_service = email_service

    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        verification_link: str | None = None,
    ) -> EmailResult:
        """Send welcome email to new user."""
        return await self._email_service.send_template(
            to=[to_email],
            template_id="welcome",
            template_data={
                "user_name": user_name,
                "verification_link": verification_link,
            },
            subject=f"Welcome, {user_name}!",
        )

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        expires_in_minutes: int = 60,
    ) -> EmailResult:
        """Send password reset email."""
        return await self._email_service.send_template(
            to=[to_email],
            template_id="password_reset",
            template_data={
                "reset_link": reset_link,
                "expires_in_minutes": expires_in_minutes,
            },
            subject="Reset Your Password",
        )

    async def send_verification_email(
        self,
        to_email: str,
        verification_code: str,
    ) -> EmailResult:
        """Send email verification code."""
        return await self._email_service.send_template(
            to=[to_email],
            template_id="verification",
            template_data={
                "verification_code": verification_code,
            },
            subject="Verify Your Email",
        )

    async def send_notification_email(
        self,
        to_email: str,
        title: str,
        message: str,
        action_url: str | None = None,
        action_text: str | None = None,
    ) -> EmailResult:
        """Send notification email."""
        return await self._email_service.send_template(
            to=[to_email],
            template_id="notification",
            template_data={
                "title": title,
                "message": message,
                "action_url": action_url,
                "action_text": action_text,
            },
            subject=title,
        )
```

### Email Templates

```html
<!-- app/templates/email/base.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #eee;
        }
        .content {
            padding: 30px 0;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #4F46E5;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
        }
        .footer {
            text-align: center;
            padding: 20px 0;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        {% block header %}
        <h1>{{ app_name | default("App") }}</h1>
        {% endblock %}
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <div class="footer">
        {% block footer %}
        <p>&copy; {{ year | default("2025") }} {{ app_name | default("App") }}. All rights reserved.</p>
        {% endblock %}
    </div>
</body>
</html>
```

```html
<!-- app/templates/email/welcome.html -->
{% extends "base.html" %}

{% block content %}
<h2>Welcome, {{ user_name }}!</h2>
<p>We're excited to have you on board. Your account has been successfully created.</p>

{% if verification_link %}
<p>Please verify your email address by clicking the button below:</p>
<p style="text-align: center; margin: 30px 0;">
    <a href="{{ verification_link }}" class="button">Verify Email</a>
</p>
{% endif %}

<p>If you have any questions, feel free to reply to this email.</p>
<p>Best regards,<br>The Team</p>
{% endblock %}
```

```html
<!-- app/templates/email/password_reset.html -->
{% extends "base.html" %}

{% block content %}
<h2>Reset Your Password</h2>
<p>We received a request to reset your password. Click the button below to create a new password:</p>

<p style="text-align: center; margin: 30px 0;">
    <a href="{{ reset_link }}" class="button">Reset Password</a>
</p>

<p>This link will expire in {{ expires_in_minutes }} minutes.</p>

<p>If you didn't request this, you can safely ignore this email.</p>
{% endblock %}
```

### Email Dependencies

```python
# app/api/v1/dependencies/email.py
from typing import Annotated

from fastapi import Depends

from app.application.services.email import EmailApplicationService
from app.core.config import settings
from app.domain.services.email import EmailService
from app.infrastructure.email.smtp import SMTPEmailService
from app.infrastructure.email.resend_service import ResendEmailService
from app.infrastructure.email.sendgrid_service import SendGridEmailService


def get_email_service() -> EmailService:
    """Get email service based on configuration."""
    if settings.EMAIL_PROVIDER == "resend":
        return ResendEmailService()
    elif settings.EMAIL_PROVIDER == "sendgrid":
        return SendGridEmailService()
    return SMTPEmailService()


def get_email_app_service(
    email_service: EmailService = Depends(get_email_service),
) -> EmailApplicationService:
    """Get email application service."""
    return EmailApplicationService(email_service)


EmailSvc = Annotated[EmailApplicationService, Depends(get_email_app_service)]
```

### Environment Settings

```python
# Add to app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # Email Configuration
    EMAIL_PROVIDER: Literal["smtp", "resend", "sendgrid"] = "smtp"
    EMAIL_FROM: str = "noreply@example.com"

    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    # Resend Settings
    RESEND_API_KEY: str = ""

    # SendGrid Settings
    SENDGRID_API_KEY: str = ""
```

## Dependencies

```toml
# Add to pyproject.toml
dependencies = [
    # ... existing ...
    "aiosmtplib>=3.0.0",      # Async SMTP
    "resend>=2.0.0",           # Resend API
    "sendgrid>=6.11.0",        # SendGrid API
    "jinja2>=3.1.0",           # Template rendering
]
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
