import os
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from PIL import Image


def phone_number_validator(value):
    """Validate Iranian phone number format"""
    if not value:
        return
    
    # Remove any spaces or special characters
    cleaned_value = re.sub(r'[^\d]', '', str(value))
    
    # Check if it's a valid Iranian mobile number
    if not re.match(r'^09\d{9}$', cleaned_value):
        raise ValidationError(_('Enter a valid Iranian phone number starting with 09 (e.g., 09123456789)'))


def avatar_validator(file):
    """Validate uploaded avatar image"""
    if not file:
        return
    
    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError(_('File too large. Maximum size is 5MB.'))
    
    # Check file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(_('Unsupported file format. Allowed formats: JPG, PNG, WebP, GIF'))
    
    # Check image dimensions and content
    try:
        with Image.open(file) as img:
            # Check if it's actually an image
            img.verify()
            
            # Reset file pointer
            file.seek(0)
            
            # Check dimensions
            img = Image.open(file)
            width, height = img.size
            
            # Minimum dimensions
            if width < 100 or height < 100:
                raise ValidationError(_('Image too small. Minimum dimensions are 100x100 pixels.'))
            
            # Maximum dimensions
            if width > 2048 or height > 2048:
                raise ValidationError(_('Image too large. Maximum dimensions are 2048x2048 pixels.'))
            
            # Check aspect ratio (not too extreme)
            aspect_ratio = width / height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                raise ValidationError(_('Image aspect ratio too extreme. Please use a more square image.'))
                
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError(_('Invalid image file. Please upload a valid image.'))


def username_validator(value):
    """Validate username format"""
    if not value:
        return
    
    # Username should be 3-30 characters
    if len(value) < 3:
        raise ValidationError(_('Username must be at least 3 characters long.'))
    
    if len(value) > 30:
        raise ValidationError(_('Username must be no more than 30 characters long.'))
    
    # Username should only contain letters, numbers, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValidationError(_('Username can only contain letters, numbers, underscores, and hyphens.'))
    
    # Username should start with a letter or number
    if not re.match(r'^[a-zA-Z0-9]', value):
        raise ValidationError(_('Username must start with a letter or number.'))
    
    # Username should not end with underscore or hyphen
    if value.endswith('_') or value.endswith('-'):
        raise ValidationError(_('Username cannot end with underscore or hyphen.'))
    
    # Check for reserved usernames
    reserved_usernames = [
        'admin', 'administrator', 'root', 'user', 'users', 'api', 'www', 'mail', 'email',
        'support', 'help', 'about', 'contact', 'privacy', 'terms', 'login', 'logout',
        'register', 'signup', 'signin', 'dashboard', 'profile', 'settings', 'account',
        'blog', 'blogs', 'post', 'posts', 'category', 'categories', 'tag', 'tags',
        'search', 'home', 'index', 'main', 'news', 'feed', 'rss', 'sitemap'
    ]
    
    if value.lower() in reserved_usernames:
        raise ValidationError(_('This username is reserved and cannot be used.'))


def bio_validator(value):
    """Validate bio content"""
    if not value:
        return
    
    # Check length
    if len(value) > 500:
        raise ValidationError(_('Bio must be no more than 500 characters long.'))
    
    # Check for inappropriate content (basic check)
    inappropriate_words = ['spam', 'scam', 'fake', 'bot']  # Add more as needed
    if any(word in value.lower() for word in inappropriate_words):
        raise ValidationError(_('Bio contains inappropriate content.'))


def social_url_validator(value):
    """Validate social media URLs"""
    if not value:
        return
    
    # Basic URL validation
    validator = URLValidator()
    try:
        validator(value)
    except ValidationError:
        raise ValidationError(_('Please enter a valid URL.'))
    
    # Check for common social media domains
    social_domains = [
        'twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com',
        'github.com', 'youtube.com', 'tiktok.com', 'snapchat.com',
        'pinterest.com', 'reddit.com', 'discord.com', 'telegram.org'
    ]
    
    # Extract domain from URL
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if it's a valid social media domain
        if not any(social_domain in domain for social_domain in social_domains):
            raise ValidationError(_('Please enter a valid social media URL.'))
            
    except Exception:
        raise ValidationError(_('Please enter a valid social media URL.'))


def password_strength_validator(value):
    """Validate password strength"""
    if not value:
        return
    
    # Check minimum length
    if len(value) < 8:
        raise ValidationError(_('Password must be at least 8 characters long.'))
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('Password must contain at least one lowercase letter.'))
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('Password must contain at least one uppercase letter.'))
    
    # Check for at least one digit
    if not re.search(r'\d', value):
        raise ValidationError(_('Password must contain at least one number.'))
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', value):
        raise ValidationError(_('Password must contain at least one special character.'))
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey'
    ]
    
    if value.lower() in weak_passwords:
        raise ValidationError(_('This password is too common. Please choose a stronger password.'))
