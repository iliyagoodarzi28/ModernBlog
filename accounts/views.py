from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView, RedirectView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import logging

from .forms import (
    CustomAuthenticationForm, CustomUserCreationForm, ProfileUpdateForm,
    PasswordChangeForm, EmailChangeForm
)
from .models import CustomUser
from .utils import get_user_stats, get_recent_activities, calculate_age
from .signals import user_profile_updated

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    """Enhanced login view with better UX"""
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        """Handle successful login"""
        user = form.get_user()
        
        # Update last activity
        user.update_last_activity()
        
        # Set remember me session
        if form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        else:
            self.request.session.set_expiry(0)  # Session expires when browser closes
        
        messages.success(self.request, _("Welcome back, {}!").format(user.get_display_name()))
        logger.info(f"User {user.email} logged in successfully")
        
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle failed login"""
        messages.error(self.request, _("Invalid email or password. Please try again."))
        logger.warning(f"Failed login attempt for email: {form.cleaned_data.get('username', 'unknown')}")
        return super().form_invalid(form)

    def get_success_url(self):
        """Get the success URL after login"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url


class CustomLogoutView(LogoutView):
    """Enhanced logout view with direct logout"""
    next_page = reverse_lazy('main:home')
    http_method_names = ['get', 'post', 'options', 'head', 'delete', 'put', 'patch']

    def get(self, request, *args, **kwargs):
        """Handle GET request for logout - logout directly without confirmation"""
        if request.user.is_authenticated:
            logger.info(f"User {request.user.email} logged out")
            messages.info(request, _("You have been logged out successfully."))
        
        # Logout the user and redirect immediately
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.next_page)

    def post(self, request, *args, **kwargs):
        """Handle POST request for logout"""
        if request.user.is_authenticated:
            logger.info(f"User {request.user.email} logged out")
            messages.info(request, _("You have been logged out successfully."))
        
        # Logout the user and redirect immediately
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.next_page)


class CustomRegisterView(CreateView):
    """Enhanced registration view"""
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        """Handle successful registration"""
        try:
            with transaction.atomic():
                user = form.save()
                
                # Log the user in automatically
                login(self.request, user)
                
                # Update last activity
                user.update_last_activity()
                
                messages.success(
                    self.request, 
                    _("Welcome to ModernBlog, {}! Your account has been created successfully.").format(
                        user.get_display_name()
                    )
                )
                
                logger.info(f"New user registered: {user.email}")
                
                # Send welcome email (if configured)
                self.send_welcome_email(user)
                
                return HttpResponseRedirect(self.get_success_url())
                
        except Exception as e:
            logger.error(f"Registration error for {form.cleaned_data.get('email')}: {str(e)}")
            messages.error(self.request, _("There was an error creating your account. Please try again."))
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle failed registration"""
        messages.error(self.request, _("Please correct the errors below and try again."))
        logger.warning(f"Registration failed for email: {form.cleaned_data.get('email', 'unknown')}")
        return super().form_invalid(form)

    def send_welcome_email(self, user):
        """Send welcome email to new user"""
        try:
            # This would be implemented with your email backend
            # from django.core.mail import send_mail
            # send_mail(
            #     _('Welcome to ModernBlog!'),
            #     _('Thank you for joining our community.'),
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            #     fail_silently=False,
            # )
            pass
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")


class ProfileView(LoginRequiredMixin, TemplateView):
    """Enhanced profile view with comprehensive user data"""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Update last activity
        user.update_last_activity()
        
        # Get user statistics
        stats = get_user_stats(user)
        
        # Get recent activities
        recent_activities = get_recent_activities(user, limit=10)
        
        # Get user posts (if blog app is available)
        try:
            from blog.models import Blog
            user_posts = Blog.objects.filter(
                author=user, 
                is_active=True
            ).order_by('-created_at')[:6]
        except ImportError:
            user_posts = []
        
        context.update({
            'user': user,
            'age': calculate_age(user.birth_date),
            'user_stats': stats,
            'recent_activities': recent_activities,
            'user_posts': user_posts,
            'user_posts_count': stats['posts_count'],
            'user_followers_count': stats['followers_count'],
            'user_following_count': stats['following_count'],
            'total_views': stats['total_views'],
            'social_links': user.get_social_links(),
            'is_own_profile': True,
        })
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Enhanced profile update view"""
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        """Handle successful profile update"""
        try:
            with transaction.atomic():
                user = form.save()
                
                # Update last activity
                user.update_last_activity()
                
                # Send signal for profile update
                user_profile_updated.send(sender=self.__class__, user=user, request=self.request)
                
                messages.success(self.request, _("Your profile has been updated successfully."))
                logger.info(f"Profile updated for user: {user.email}")
                
                return HttpResponseRedirect(self.get_success_url())
                
        except Exception as e:
            logger.error(f"Profile update error for {self.request.user.email}: {str(e)}")
            messages.error(self.request, _("There was an error updating your profile. Please try again."))
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle failed profile update"""
        messages.error(self.request, _("Please correct the errors below and try again."))
        return super().form_invalid(form)


class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Enhanced password change view"""
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')

    def form_valid(self, form):
        """Handle successful password change"""
        try:
            with transaction.atomic():
                user = form.save()
                
                # Update session hash to prevent logout
                update_session_auth_hash(self.request, user)
                
                # Update last activity
                user.update_last_activity()
                
                messages.success(self.request, _("Your password has been changed successfully."))
                logger.info(f"Password changed for user: {user.email}")
                
                return HttpResponseRedirect(self.get_success_url())
                
        except Exception as e:
            logger.error(f"Password change error for {self.request.user.email}: {str(e)}")
            messages.error(self.request, _("There was an error changing your password. Please try again."))
            return self.form_invalid(form)


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    """Password change confirmation view"""
    template_name = 'accounts/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class EmailChangeView(LoginRequiredMixin, TemplateView):
    """Email change view"""
    template_name = 'accounts/email_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EmailChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = EmailChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_email = form.cleaned_data['new_email']
                    old_email = request.user.email
                    
                    # Update email
                    request.user.email = new_email
                    request.user.save()
                    
                    # Update last activity
                    request.user.update_last_activity()
                    
                    messages.success(
                        request, 
                        _("Your email address has been changed from {} to {}.").format(
                            old_email, new_email
                        )
                    )
                    
                    logger.info(f"Email changed for user {old_email} to {new_email}")
                    
                    return redirect('accounts:profile')
                    
            except Exception as e:
                logger.error(f"Email change error for {request.user.email}: {str(e)}")
                messages.error(request, _("There was an error changing your email. Please try again."))
        else:
            messages.error(request, _("Please correct the errors below and try again."))
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    """Account settings view"""
    template_name = 'accounts/account_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'user': user,
            'account_age': (timezone.now() - user.date_joined).days,
            'last_login': user.last_login,
            'is_verified': user.is_verified,
            'is_premium': user.is_premium,
        })
        
        return context


class AccountDeactivationView(LoginRequiredMixin, TemplateView):
    """Account deactivation view"""
    template_name = 'accounts/account_deactivation.html'

    def post(self, request, *args, **kwargs):
        """Handle account deactivation"""
        if request.POST.get('confirm_deactivation') == 'yes':
            try:
                with transaction.atomic():
                    user = request.user
                    user.is_active = False
                    user.save()
                    
                    logger.info(f"Account deactivated for user: {user.email}")
                    messages.success(request, _("Your account has been deactivated successfully."))
                    
                    return redirect('accounts:login')
                    
            except Exception as e:
                logger.error(f"Account deactivation error for {request.user.email}: {str(e)}")
                messages.error(request, _("There was an error deactivating your account. Please try again."))
        else:
            messages.error(request, _("Please confirm that you want to deactivate your account."))
        
        return self.get(request, *args, **kwargs)


# API Views for AJAX requests
@method_decorator(login_required, name='dispatch')
class UserStatsAPIView(TemplateView):
    """API view for user statistics"""
    
    def get(self, request, *args, **kwargs):
        stats = get_user_stats(request.user)
        return JsonResponse(stats)


@method_decorator(login_required, name='dispatch')
class UserActivityAPIView(TemplateView):
    """API view for user activities"""
    
    def get(self, request, *args, **kwargs):
        limit = request.GET.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        activities = get_recent_activities(request.user, limit=limit)
        return JsonResponse({'activities': activities})


@require_POST
@login_required
def update_last_activity(request):
    """Update user's last activity timestamp"""
    try:
        request.user.update_last_activity()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Failed to update last activity for {request.user.email}: {str(e)}")
        return JsonResponse({'status': 'error'}, status=500)


@require_POST
@login_required
def toggle_profile_privacy(request):
    """Toggle profile privacy setting"""
    try:
        user = request.user
        user.profile_public = not user.profile_public
        user.save()
        
        status = 'public' if user.profile_public else 'private'
        messages.success(request, _("Your profile is now {}.").format(status))
        
        return JsonResponse({
            'status': 'success',
            'is_public': user.profile_public
        })
    except Exception as e:
        logger.error(f"Failed to toggle privacy for {request.user.email}: {str(e)}")
        return JsonResponse({'status': 'error'}, status=500)