from django.urls import path
from .views import ContactView, NewsletterView, newsletter_ajax
from django.views.generic import TemplateView

app_name = 'contact'

urlpatterns = [
    path('', ContactView.as_view(), name='contact'),
    path('success/', TemplateView.as_view(template_name='contact/success.html'), name='success'),
    path('newsletter/', NewsletterView.as_view(), name='newsletter'),
    path('newsletter/ajax/', newsletter_ajax, name='newsletter_ajax'),
]
