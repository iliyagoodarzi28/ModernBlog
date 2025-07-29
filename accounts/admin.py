from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'gender']
    ordering = ['-date_joined']
    search_fields = ['email', 'username', 'full_name', 'phone']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_("Personal Information"), {
            'fields': ('full_name', 'avatar', 'gender', 'birth_date', 'phone')
        }),
        (_("Permissions"), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_("Important Dates"), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'is_staff', 'is_active'
            ),
        }),
    )
