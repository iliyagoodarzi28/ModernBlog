"""
Custom adapter for django-allauth to work with our CustomUser model
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for allauth"""
    
    def save_user(self, request, user, form, commit=True):
        """Save user with additional fields"""
        user = super().save_user(request, user, form, commit=False)
        
        # Add custom fields
        if 'full_name' in form.cleaned_data:
            user.full_name = form.cleaned_data['full_name']
        if 'phone' in form.cleaned_data:
            user.phone = form.cleaned_data['phone']
        if 'gender' in form.cleaned_data:
            user.gender = form.cleaned_data['gender']
        if 'birth_date' in form.cleaned_data:
            user.birth_date = form.cleaned_data['birth_date']
        
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for allauth"""
    
    def populate_user(self, request, sociallogin, data):
        """Populate user with social account data"""
        user = super().populate_user(request, sociallogin, data)
        
        # Extract additional data from social account
        extra_data = sociallogin.account.extra_data
        
        # Set full name from social data
        if 'name' in extra_data:
            user.full_name = extra_data['name']
        elif 'first_name' in extra_data and 'last_name' in extra_data:
            user.full_name = f"{extra_data['first_name']} {extra_data['last_name']}"
        
        # Set profile picture if available
        if 'picture' in extra_data:
            user.profile_picture = extra_data['picture']
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """Handle pre-social login logic"""
        # Check if user already exists with this email
        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email')
            if email and CustomUser.objects.filter(email=email).exists():
                # User exists, link the social account
                user = CustomUser.objects.get(email=email)
                sociallogin.connect(request, user)
                messages.success(request, _("Your Google account has been linked successfully!"))
                raise ImmediateHttpResponse(redirect('/accounts/profile/'))
        
        elif sociallogin.account.provider == 'facebook':
            email = sociallogin.account.extra_data.get('email')
            if email and CustomUser.objects.filter(email=email).exists():
                # User exists, link the social account
                user = CustomUser.objects.get(email=email)
                sociallogin.connect(request, user)
                messages.success(request, _("Your Facebook account has been linked successfully!"))
                raise ImmediateHttpResponse(redirect('/accounts/profile/'))
    
    def save_user(self, request, sociallogin, form=None):
        """Save user from social login"""
        user = super().save_user(request, sociallogin, form)
        
        # Update last activity
        user.update_last_activity()
        
        # Log the registration
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"New user registered via {sociallogin.account.provider}: {user.email}")
        
        return user
