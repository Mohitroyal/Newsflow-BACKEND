import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import email_service

def test_email_service_mock_fallback():
    # When SMTP is not configured, it should return True (simulated success)
    with patch("app.services.email_service.settings") as mock_settings:
        mock_settings.SMTP_HOST = None
        mock_settings.SMTP_USER = None
        
        result = email_service.send_clipping_status_email(
            user_email="test@example.com",
            headline="Mock Headline Test",
            status="completed",
            png_url="http://example.com/test.png",
            pdf_url="http://example.com/test.pdf"
        )
        assert result is True

def test_email_service_smtp_success():
    # Test path when SMTP is configured
    with patch("app.services.email_service.settings") as mock_settings, \
         patch("smtplib.SMTP") as mock_smtp_class:
        
        mock_settings.SMTP_HOST = "smtp.mailtrap.io"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user123"
        mock_settings.SMTP_PASSWORD = "password123"
        mock_settings.SMTP_TLS = True
        mock_settings.EMAILS_FROM_EMAIL = "noreply@newscraft.ai"
        
        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value = mock_smtp_instance
        
        # Test success email
        result = email_service.send_clipping_status_email(
            user_email="test@example.com",
            headline="SMTP Success Test",
            status="completed",
            png_url="http://example.com/test.png",
            pdf_url="http://example.com/test.pdf"
        )
        
        assert result is True
        mock_smtp_class.assert_called_once_with("smtp.mailtrap.io", 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("user123", "password123")
        mock_smtp_instance.sendmail.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()

def test_email_service_failure_path():
    # Test failure path when SMTP is configured but fails to connect
    with patch("app.services.email_service.settings") as mock_settings, \
         patch("smtplib.SMTP") as mock_smtp_class:
        
        mock_settings.SMTP_HOST = "smtp.mailtrap.io"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user123"
        mock_settings.SMTP_PASSWORD = "password123"
        mock_settings.SMTP_TLS = True
        
        mock_smtp_class.side_effect = Exception("SMTP Connection Refused")
        
        # Should return False on exception
        result = email_service.send_clipping_status_email(
            user_email="test@example.com",
            headline="SMTP Failure Test",
            status="failed"
        )
        
        assert result is False
