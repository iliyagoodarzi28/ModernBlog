"""
Management command to create social applications for Google and Facebook
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Create social applications for Google and Facebook'

    def handle(self, *args, **options):
        # Get the current site
        site = Site.objects.get_current()
        
        # Create Google application
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': 'your-google-client-id',
                'secret': 'your-google-client-secret',
            }
        )
        if created:
            google_app.sites.add(site)
            self.stdout.write(
                self.style.SUCCESS('Google social application created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Google social application already exists')
            )
        
        # Create Facebook application
        facebook_app, created = SocialApp.objects.get_or_create(
            provider='facebook',
            defaults={
                'name': 'Facebook',
                'client_id': 'your-facebook-app-id',
                'secret': 'your-facebook-app-secret',
            }
        )
        if created:
            facebook_app.sites.add(site)
            self.stdout.write(
                self.style.SUCCESS('Facebook social application created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Facebook social application already exists')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nSocial applications created! Please update the client_id and secret '
                'in the Django admin panel with your actual OAuth credentials.\n'
                'Admin URL: /admin/socialaccount/socialapp/'
            )
        )
