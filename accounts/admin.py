from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter

from .models import CustomUser
from .utils import get_user_stats


class LastActivityFilter(SimpleListFilter):
    """Filter users by last activity"""
    title = _('Last Activity')
    parameter_name = 'last_activity'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('week', _('This Week')),
            ('month', _('This Month')),
            ('year', _('This Year')),
            ('never', _('Never')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(last_activity__date=now.date())
        elif self.value() == 'week':
            week_ago = now - timezone.timedelta(days=7)
            return queryset.filter(last_activity__gte=week_ago)
        elif self.value() == 'month':
            month_ago = now - timezone.timedelta(days=30)
            return queryset.filter(last_activity__gte=month_ago)
        elif self.value() == 'year':
            year_ago = now - timezone.timedelta(days=365)
            return queryset.filter(last_activity__gte=year_ago)
        elif self.value() == 'never':
            return queryset.filter(last_activity__isnull=True)


class AccountStatusFilter(SimpleListFilter):
    """Filter users by account status"""
    title = _('Account Status')
    parameter_name = 'account_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
            ('verified', _('Verified')),
            ('premium', _('Premium')),
            ('recent', _('Recently Joined')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        elif self.value() == 'verified':
            return queryset.filter(is_verified=True)
        elif self.value() == 'premium':
            return queryset.filter(is_premium=True)
        elif self.value() == 'recent':
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            return queryset.filter(date_joined__gte=thirty_days_ago)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Enhanced user admin with better organization and functionality"""
    
    model = CustomUser
    
    # List display
    list_display = [
        'email', 'username', 'get_display_name', 'is_staff', 'is_active', 
        'is_verified', 'is_premium', 'get_last_activity', 'date_joined'
    ]
    
    # List filters
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'is_verified', 'is_premium',
        'gender', 'profile_public', LastActivityFilter, AccountStatusFilter,
        'date_joined'
    ]
    
    # Search fields
    search_fields = ['email', 'username', 'full_name', 'phone']
    
    # Ordering
    ordering = ['-date_joined']
    
    # Fieldsets for user edit form
    fieldsets = (
        (_("Authentication"), {
            'fields': ('email', 'username', 'password')
        }),
        (_("Personal Information"), {
            'fields': ('full_name', 'avatar', 'gender', 'birth_date', 'phone', 'bio', 'location')
        }),
        (_("Social Media"), {
            'fields': ('website', 'twitter', 'facebook', 'instagram', 'linkedin', 'github', 'youtube'),
            'classes': ('collapse',)
        }),
        (_("Privacy Settings"), {
            'fields': ('profile_public', 'show_email', 'allow_messages'),
            'classes': ('collapse',)
        }),
        (_("Account Status"), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'is_premium')
        }),
        (_("Groups & Permissions"), {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_("Important Dates"), {
            'fields': ('last_login', 'last_activity', 'date_joined', 'updated_at')
        }),
    )
    
    # Fieldsets for user creation form
    add_fieldsets = (
        (_("Required Information"), {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'is_staff', 'is_active', 'is_verified'
            ),
        }),
        (_("Optional Information"), {
            'classes': ('wide', 'collapse'),
            'fields': (
                'full_name', 'phone', 'gender', 'birth_date', 'avatar',
                'bio', 'location', 'website'
            ),
        }),
    )
    
    # Read-only fields
    readonly_fields = ['date_joined', 'last_login', 'last_activity', 'updated_at']
    
    # Actions
    actions = ['make_verified', 'make_premium', 'deactivate_users', 'activate_users', 'export_user_data']
    
    def get_display_name(self, obj):
        """Get user's display name"""
        return obj.get_display_name()
    get_display_name.short_description = _('Display Name')
    get_display_name.admin_order_field = 'full_name'
    
    def get_last_activity(self, obj):
        """Get formatted last activity"""
        if obj.last_activity:
            return obj.last_activity.strftime('%Y-%m-%d %H:%M')
        return _('Never')
    get_last_activity.short_description = _('Last Activity')
    get_last_activity.admin_order_field = 'last_activity'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return super().get_queryset(request).select_related().prefetch_related('groups', 'user_permissions')
    
    def get_readonly_fields(self, request, obj=None):
        """Make email readonly for existing users"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editing existing user
            readonly_fields.append('email')
        return readonly_fields
    
    # Custom actions
    def make_verified(self, request, queryset):
        """Mark selected users as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            _('{} users have been marked as verified.').format(updated)
        )
    make_verified.short_description = _('Mark selected users as verified')
    
    def make_premium(self, request, queryset):
        """Mark selected users as premium"""
        updated = queryset.update(is_premium=True)
        self.message_user(
            request,
            _('{} users have been marked as premium.').format(updated)
        )
    make_premium.short_description = _('Mark selected users as premium')
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _('{} users have been deactivated.').format(updated)
        )
    deactivate_users.short_description = _('Deactivate selected users')
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('{} users have been activated.').format(updated)
        )
    activate_users.short_description = _('Activate selected users')
    
    def export_user_data(self, request, queryset):
        """Export user data (placeholder for CSV export)"""
        # This would implement CSV export functionality
        self.message_user(
            request,
            _('User data export functionality would be implemented here.')
        )
    export_user_data.short_description = _('Export user data')
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on user permissions"""
        form = super().get_form(request, obj, **kwargs)
        
        # Hide superuser fields for non-superusers
        if not request.user.is_superuser:
            if 'is_superuser' in form.base_fields:
                del form.base_fields['is_superuser']
            if 'user_permissions' in form.base_fields:
                del form.base_fields['user_permissions']
        
        return form
    
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        if not change:  # Creating new user
            obj.last_activity = timezone.now()
        
        super().save_model(request, obj, form, change)
        
        # Log admin action
        if change:
            self.log_change(request, obj, [])
        else:
            self.log_addition(request, obj, [])


# Custom admin site configuration
admin.site.site_header = _('ModernBlog Administration')
admin.site.site_title = _('ModernBlog Admin')
admin.site.index_title = _('Welcome to ModernBlog Administration')
