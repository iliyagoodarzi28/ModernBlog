# accounts/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

from .models import CustomUser


@receiver(post_delete, sender=CustomUser)
def delete_user_avatar(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
