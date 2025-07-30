from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager





class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=150, blank=True, verbose_name="Full Name")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True, verbose_name="Profile Picture")

    GENDER_CHOICES = (
        ('male', 'Man'),
        ('female', 'Woman'),
        ('other', 'Other')
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Gender")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Date Of Birth")

    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


