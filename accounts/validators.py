import os
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def phone_number_validator(value):

    if not re.match(r'^09\d{9}$', str(value)):
        raise ValidationError(_('Enter a valid phone number starting with 09.'))

def avatar_validator(file):

    max_size = 2 * 1024 * 1024  # 2MB
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed: jpg, jpeg, png, webp'))

    if file.size > max_size:
        raise ValidationError(_('File too large. Max size is 2MB.'))
