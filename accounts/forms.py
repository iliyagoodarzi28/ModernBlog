from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'username',
            'full_name',
            'phone',
            'gender',
            'birth_date',
            'avatar'
        ]
        widgets = {
            'birth_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',  # For Bootstrap styling
                    'placeholder': 'Select your birth date',
                    'min': '1900-01-01',
                    'max': '2025-12-31'
                }
            ),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # Use email instead of username


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'full_name',
            'phone',
            'gender',
            'birth_date',
            'avatar'
        ]
        widgets = {
            'birth_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Your birth date',
                    'min': '1900-01-01',
                    'max': '2025-12-31'
                }
            ),
        }
