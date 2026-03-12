# accounts/pipeline.py

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from .models import Profile

def validate_cvsu_email(backend, details, user=None, *args, **kwargs):
    """
    Only allow @cvsu.edu.ph email addresses for Google OAuth
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    
    email = details.get('email', '')
    print(f"[PIPELINE] Validating email: {email}")  # Debug log
    
    if not email:
        print(f"[PIPELINE] No email provided!")
        raise PermissionDenied('Email address is required.')
    
    if not email.endswith('@cvsu.edu.ph'):
        print(f"[PIPELINE] Invalid email domain: {email}")
        raise PermissionDenied('Only @cvsu.edu.ph email addresses are allowed. Please use your CVSU email.')
    
    print(f"[PIPELINE] Email validated successfully: {email}")
    return None

def create_profile(backend, user, response, *args, **kwargs):
    """
    Create a Profile for users who sign in with Google OAuth
    All Google OAuth signups create student accounts
    """
    if user:
        print(f"[PIPELINE] Creating profile for user: {user.username} ({user.email})")
        
        # Check if profile already exists
        try:
            profile = user.profile
            print(f"[PIPELINE] Profile already exists: {profile.user_type}")
        except Profile.DoesNotExist:
            # All Google OAuth users are created as students
            profile = Profile.objects.create(
                user=user,
                user_type='student'
            )
            print(f"[PIPELINE] Profile created successfully: student")
    else:
        print(f"[PIPELINE] No user provided to create_profile")
    
    return None

def check_cvsu_email(backend, details, user=None, request=None, *args, **kwargs):
    email = details.get('email')
    if not email.endswith('@cvsu.edu.ph'):
        raise PermissionDenied("Only @cvsu.edu.ph emails are allowed.")

    if user:
        user.is_active = False
        user.save()

        # Send email verification
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        domain = get_current_site(request).domain
        verify_url = f"http://{domain}{reverse('verify_email', args=[uid, token])}"

        subject = "Verify your CVSU email"
        message = render_to_string('verify_email.html', {
            'user': user,
            'verify_url': verify_url,
        })

        send_mail(subject, message, 'noreply@cvsu.edu.ph', [user.email])
