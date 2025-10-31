# Social Authentication Setup Guide

This guide will help you set up Google and Facebook OAuth authentication for your Django blog application.

## Prerequisites

- Django project with django-allauth installed
- Google Cloud Console account
- Facebook Developer account

## Google OAuth2 Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API

### 2. Create OAuth2 Credentials

1. Navigate to "Credentials" in the Google Cloud Console
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/` (for development)
   - `https://yourdomain.com/accounts/google/login/callback/` (for production)
5. Copy the Client ID and Client Secret

### 3. Configure Django Settings

Add your Google credentials to environment variables:

```bash
# For development, you can set these in your .env file
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
```

Or update them directly in the Django admin:
1. Go to `/admin/socialaccount/socialapp/`
2. Edit the Google application
3. Update Client ID and Secret

## Facebook OAuth2 Setup

### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Create App"
3. Choose "Consumer" or "Other" app type
4. Fill in app details

### 2. Configure Facebook Login

1. In your Facebook app dashboard, go to "Products"
2. Add "Facebook Login" product
3. Go to "Facebook Login" → "Settings"
4. Add valid OAuth redirect URIs:
   - `http://localhost:8000/accounts/facebook/login/callback/` (for development)
   - `https://yourdomain.com/accounts/facebook/login/callback/` (for production)

### 3. Get App Credentials

1. Go to "Settings" → "Basic"
2. Copy App ID and App Secret
3. Add your domain to "App Domains"

### 4. Configure Django Settings

Add your Facebook credentials to environment variables:

```bash
# For development, you can set these in your .env file
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

Or update them directly in the Django admin:
1. Go to `/admin/socialaccount/socialapp/`
2. Edit the Facebook application
3. Update App ID and Secret

## Testing Social Authentication

### 1. Start Development Server

```bash
python manage.py runserver
```

### 2. Test Login/Registration

1. Go to `http://localhost:8000/accounts/login/`
2. Click "Google" or "Facebook" button
3. Complete OAuth flow
4. User should be redirected back and logged in

### 3. Check User Creation

1. Go to Django admin: `/admin/accounts/customuser/`
2. Verify new users are created with social account data
3. Check social accounts: `/admin/socialaccount/socialaccount/`

## Production Considerations

### 1. Environment Variables

Set up proper environment variables in production:

```bash
export GOOGLE_OAUTH2_CLIENT_ID="your-production-client-id"
export GOOGLE_OAUTH2_CLIENT_SECRET="your-production-client-secret"
export FACEBOOK_APP_ID="your-production-app-id"
export FACEBOOK_APP_SECRET="your-production-app-secret"
```

### 2. HTTPS Required

- Facebook requires HTTPS in production
- Update redirect URIs to use HTTPS
- Ensure your production server has SSL certificate

### 3. Domain Configuration

- Add your production domain to Google OAuth2 authorized origins
- Add your production domain to Facebook app domains
- Update Django `ALLOWED_HOSTS` setting

### 4. Security Settings

Update settings for production:

```python
# In production settings
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**
   - Check that redirect URIs match exactly in OAuth provider settings
   - Ensure protocol (http/https) matches

2. **"App not configured"**
   - Verify app is published (Facebook)
   - Check app domains and redirect URIs

3. **"Access denied"**
   - User may have denied permissions
   - Check OAuth scopes in settings

4. **"User already exists"**
   - Social account linking should handle this automatically
   - Check custom adapter implementation

### Debug Mode

Enable debug logging for social authentication:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Features Implemented

✅ Google OAuth2 authentication
✅ Facebook OAuth2 authentication  
✅ Automatic user creation from social accounts
✅ Social account linking for existing users
✅ Custom user model integration
✅ Profile data extraction from social accounts
✅ Secure redirect handling
✅ Production-ready configuration

## Next Steps

1. Set up OAuth credentials for your providers
2. Test authentication flows
3. Customize user data extraction as needed
4. Deploy to production with proper HTTPS setup
5. Monitor authentication logs for any issues
