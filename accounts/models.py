from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from .managers import CustomUserManager
from .validators import phone_number_validator, avatar_validator
from .utils import GENDER_CHOICES


class CustomUser(AbstractUser):
    """
    Enhanced Custom User Model with professional features
    """
    
    # Basic Information
    email = models.EmailField(
        unique=True, 
        verbose_name=_("Email Address"),
        help_text=_("Your primary email address")
    )
    full_name = models.CharField(
        max_length=150, 
        blank=True, 
        verbose_name=_("Full Name"),
        help_text=_("Your complete name")
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[phone_number_validator], 
        verbose_name=_("Phone Number"),
        help_text=_("Your contact number")
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/', 
        blank=True, 
        null=True,
        validators=[avatar_validator], 
        verbose_name=_("Profile Picture"),
        help_text=_("Upload your profile picture")
    )
    
    # Personal Information
    gender = models.CharField(
        max_length=20, 
        choices=GENDER_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name=_("Gender")
    )
    birth_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name=_("Date of Birth"),
        help_text=_("Your birth date")
    )
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name=_("Bio"),
        help_text=_("Tell us about yourself")
    )
    location = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Location"),
        help_text=_("Your current location")
    )
    website = models.URLField(
        blank=True, 
        verbose_name=_("Website"),
        help_text=_("Your personal website or blog")
    )
    
    # Social Media Links
    twitter = models.URLField(
        blank=True, 
        verbose_name=_("Twitter"),
        help_text=_("Your Twitter profile")
    )
    facebook = models.URLField(
        blank=True, 
        verbose_name=_("Facebook"),
        help_text=_("Your Facebook profile")
    )
    instagram = models.URLField(
        blank=True, 
        verbose_name=_("Instagram"),
        help_text=_("Your Instagram profile")
    )
    linkedin = models.URLField(
        blank=True, 
        verbose_name=_("LinkedIn"),
        help_text=_("Your LinkedIn profile")
    )
    github = models.URLField(
        blank=True, 
        verbose_name=_("GitHub"),
        help_text=_("Your GitHub profile")
    )
    youtube = models.URLField(
        blank=True, 
        verbose_name=_("YouTube"),
        help_text=_("Your YouTube channel")
    )
    
    # Privacy Settings
    profile_public = models.BooleanField(
        default=True, 
        verbose_name=_("Public Profile"),
        help_text=_("Allow others to view your profile")
    )
    show_email = models.BooleanField(
        default=False, 
        verbose_name=_("Show Email"),
        help_text=_("Display email address on profile")
    )
    allow_messages = models.BooleanField(
        default=True, 
        verbose_name=_("Allow Messages"),
        help_text=_("Allow other users to send you messages")
    )
    
    # Account Status
    is_verified = models.BooleanField(
        default=False, 
        verbose_name=_("Verified Account"),
        help_text=_("Account verification status")
    )
    is_premium = models.BooleanField(
        default=False, 
        verbose_name=_("Premium Account"),
        help_text=_("Premium membership status")
    )
    
    # Timestamps
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date Joined")
    )
    last_activity = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Last Activity")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated")
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        """Get the display name for the user"""
        return self.full_name or self.username

    def get_absolute_url(self):
        """Get the absolute URL for the user's profile"""
        return reverse('accounts:profile')

    def get_avatar_url(self):
        """Get the avatar URL or return default"""
        if self.avatar:
            return self.avatar.url
        return None

    def get_age(self):
        """Calculate user's age from birth date"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def update_last_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def get_social_links(self):
        """Get all non-empty social media links"""
        social_fields = ['website', 'twitter', 'facebook', 'instagram', 'linkedin', 'github', 'youtube']
        return {field: getattr(self, field) for field in social_fields if getattr(self, field)}

    @property
    def is_active_recently(self):
        """Check if user was active in the last 30 days"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return self.last_activity >= thirty_days_ago