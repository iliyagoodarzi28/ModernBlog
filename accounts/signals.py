from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver, Signal
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import os
import logging

from .models import CustomUser

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def user_post_save(sender, instance, created, **kwargs):
    """Handle user creation and updates"""
    if created:
        # New user created
        logger.info(f"New user created: {instance.email}")
        
        # Send welcome email
        try:
            send_mail(
                _('Welcome to ModernBlog!'),
                _('Thank you for joining our community. We\'re excited to have you on board!'),
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}")
    else:
        # User updated
        logger.info(f"User updated: {instance.email}")


@receiver(pre_save, sender=CustomUser)
def user_pre_save(sender, instance, **kwargs):
    """Handle user before save"""
    # Update last activity if user is being saved
    if instance.pk:
        instance.last_activity = timezone.now()


@receiver(post_delete, sender=CustomUser)
def delete_user_avatar(sender, instance, **kwargs):
    """Delete user avatar file when user is deleted"""
    if instance.avatar:
        try:
            if os.path.isfile(instance.avatar.path):
                os.remove(instance.avatar.path)
                logger.info(f"Deleted avatar file for user: {instance.email}")
        except Exception as e:
            logger.error(f"Failed to delete avatar file for {instance.email}: {str(e)}")


# Custom signal for profile updates
user_profile_updated = Signal()


@receiver(user_profile_updated)
def handle_profile_update(sender, user, request, **kwargs):
    """Handle profile update events"""
    logger.info(f"Profile updated for user: {user.email}")
    
    # You can add additional logic here, such as:
    # - Sending notifications
    # - Updating related models
    # - Logging activity
    # - Triggering other actions
