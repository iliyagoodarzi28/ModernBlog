from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .validators import (
    username_validator, bio_validator, social_url_validator, 
    password_strength_validator
)
from .utils import get_password_strength_score


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form with better validation and styling"""
    
    email = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email address'),
            'autocomplete': 'email',
        }),
        help_text=_("We'll never share your email with anyone else.")
    )
    
    username = forms.CharField(
        label=_("Username"),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Choose a unique username'),
            'autocomplete': 'username',
        }),
        help_text=_("3-30 characters. Letters, numbers, underscores, and hyphens only."),
        validators=[username_validator]
    )
    
    full_name = forms.CharField(
        label=_("Full Name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your full name'),
            'autocomplete': 'name',
        }),
        help_text=_("Your complete name (optional)")
    )
    
    phone = forms.CharField(
        label=_("Phone Number"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('09123456789'),
            'autocomplete': 'tel',
        }),
        help_text=_("Iranian mobile number starting with 09 (optional)")
    )
    
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=[('', _('Select gender'))] + list(CustomUser._meta.get_field('gender').choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text=_("Optional")
    )
    
    birth_date = forms.DateField(
        label=_("Date of Birth"),
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': '2025-12-31',
            'min': '1900-01-01',
        }),
        help_text=_("Optional")
    )
    
    avatar = forms.ImageField(
        label=_("Profile Picture"),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        help_text=_("Upload a profile picture (JPG, PNG, WebP, GIF - max 5MB)")
    )
    
    terms_accepted = forms.BooleanField(
        label=_("I agree to the Terms of Service and Privacy Policy"),
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        error_messages={
            'required': _('You must accept the terms and conditions to continue.')
        }
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'full_name', 'phone', 'gender', 
            'birth_date', 'avatar'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Enhance password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Create a strong password'),
            'autocomplete': 'new-password',
        })
        self.fields['password1'].help_text = _(
            "Your password must contain at least 8 characters with a mix of letters, numbers, and symbols."
        )
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm your password'),
            'autocomplete': 'new-password',
        })
        self.fields['password2'].help_text = _("Enter the same password as before, for verification.")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError(_("A user with this username already exists."))
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            password_strength_validator(password1)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match."))
        
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form"""
    
    username = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email'),
            'autocomplete': 'email',
        })
    )
    
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your password'),
            'autocomplete': 'current-password',
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label=_("Remember me")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages.update({
            'required': _('Please enter your email address.'),
            'invalid': _('Please enter a valid email address.'),
        })
        self.fields['password'].error_messages.update({
            'required': _('Please enter your password.'),
        })


class ProfileUpdateForm(forms.ModelForm):
    """Enhanced profile update form"""
    
    bio = forms.CharField(
        label=_("Bio"),
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Tell us about yourself...'),
        }),
        help_text=_("Tell us about yourself (max 500 characters)"),
        validators=[bio_validator]
    )
    
    website = forms.URLField(
        label=_("Website"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://yourwebsite.com'),
        }),
        help_text=_("Your personal website or blog")
    )
    
    location = forms.CharField(
        label=_("Location"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('City, Country'),
        }),
        help_text=_("Your current location")
    )
    
    # Social media fields
    twitter = forms.URLField(
        label=_("Twitter"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://twitter.com/username'),
        }),
        validators=[social_url_validator]
    )
    
    facebook = forms.URLField(
        label=_("Facebook"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://facebook.com/username'),
        }),
        validators=[social_url_validator]
    )
    
    instagram = forms.URLField(
        label=_("Instagram"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://instagram.com/username'),
        }),
        validators=[social_url_validator]
    )
    
    linkedin = forms.URLField(
        label=_("LinkedIn"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://linkedin.com/in/username'),
        }),
        validators=[social_url_validator]
    )
    
    github = forms.URLField(
        label=_("GitHub"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://github.com/username'),
        }),
        validators=[social_url_validator]
    )
    
    youtube = forms.URLField(
        label=_("YouTube"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('https://youtube.com/channel/username'),
        }),
        validators=[social_url_validator]
    )

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'phone', 'gender', 'birth_date', 'avatar',
            'bio', 'website', 'location', 'twitter', 'facebook', 
            'instagram', 'linkedin', 'github', 'youtube',
            'profile_public', 'show_email', 'allow_messages'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your full name'),
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('09123456789'),
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': '2025-12-31',
                'min': '1900-01-01',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'profile_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'allow_messages': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text for privacy settings
        self.fields['profile_public'].help_text = _("Allow others to view your profile")
        self.fields['show_email'].help_text = _("Display email address on your profile")
        self.fields['allow_messages'].help_text = _("Allow other users to send you messages")


class PasswordChangeForm(PasswordChangeForm):
    """Enhanced password change form"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter your current password'),
        })
        
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Enter your new password'),
        })
        self.fields['new_password1'].help_text = _(
            "Your password must contain at least 8 characters with a mix of letters, numbers, and symbols."
        )
        
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm your new password'),
        })

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if password1:
            password_strength_validator(password1)
        return password1


class EmailChangeForm(forms.Form):
    """Form for changing email address"""
    
    new_email = forms.EmailField(
        label=_("New Email Address"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your new email address'),
        }),
        help_text=_("We'll send a verification email to this address.")
    )
    
    current_password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your current password'),
        }),
        help_text=_("Enter your current password to confirm this change.")
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if new_email == self.user.email:
            raise ValidationError(_("This is already your current email address."))
        
        if CustomUser.objects.filter(email=new_email).exists():
            raise ValidationError(_("A user with this email already exists."))
        
        return new_email

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError(_("Your current password is incorrect."))
        return current_password
