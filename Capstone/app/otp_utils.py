# OTP Utility Functions for SMTP Email Integration
import random
import string
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp, username):
    """Send OTP email using Django SMTP"""
    try:
        subject = "Verify Your Email - CVSU Case Tracking System"
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #0f6e43; color: white; padding: 30px 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ background: #f9f9f9; padding: 40px 30px; border: 1px solid #ddd; }}
        .otp-box {{ background: white; border: 3px solid #0f6e43; padding: 30px; text-align: center; margin: 30px 0; border-radius: 8px; }}
        .otp-code {{ font-size: 48px; font-weight: bold; color: #0f6e43; letter-spacing: 10px; font-family: 'Courier New', monospace; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; background: #f0f0f0; border-radius: 0 0 8px 8px; }}
        .info-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 CVSU Case Tracking System</h1>
        </div>
        <div class="content">
            <h2 style="color: #0f6e43;">Hello {username}!</h2>
            <p style="font-size: 16px;">Thank you for registering with CVSU Case Tracking System.</p>
            <p style="font-size: 16px;">To complete your registration, please use the following One-Time Password (OTP):</p>
            
            <div class="otp-box">
                <div class="otp-code">{otp}</div>
            </div>
            
            <div class="info-box">
                <strong>⏰ Important:</strong> This OTP will expire in <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.
            </div>
            
            <p style="font-size: 14px; color: #666;">If you didn't request this code, please ignore this email.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #666;">
                <strong>Need help?</strong><br>
                Contact CVSU Guidance Office for assistance.
            </p>
        </div>
        <div class="footer">
            <p style="margin: 5px 0;"><strong>Cavite State University - Bacoor Campus</strong></p>
            <p style="margin: 5px 0;">Guidance and Counseling Office</p>
            <p style="margin: 5px 0;">© 2026 CVSU Case Tracking System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        plain_message = f"""
Hello {username}!

Thank you for registering with CVSU Case Tracking System.

Your One-Time Password (OTP) is: {otp}

This OTP will expire in {settings.OTP_EXPIRY_MINUTES} minutes.

If you didn't request this code, please ignore this email.

---
Cavite State University - Bacoor Campus
Guidance and Counseling Office
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True, "OTP sent successfully"
    
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def is_otp_expired(created_at):
    """Check if OTP has expired"""
    expiry_time = created_at + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    return timezone.now() > expiry_time
