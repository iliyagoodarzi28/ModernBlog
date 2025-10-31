from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    
    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    
    # Password Management URLs
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Account Management URLs
    path('email/change/', views.EmailChangeView.as_view(), name='email_change'),
    path('settings/', views.AccountSettingsView.as_view(), name='account_settings'),
    path('deactivate/', views.AccountDeactivationView.as_view(), name='account_deactivation'),
    
    # API URLs
    path('api/stats/', views.UserStatsAPIView.as_view(), name='user_stats_api'),
    path('api/activities/', views.UserActivityAPIView.as_view(), name='user_activities_api'),
    path('api/update-activity/', views.update_last_activity, name='update_activity'),
    path('api/toggle-privacy/', views.toggle_profile_privacy, name='toggle_privacy'),
]
