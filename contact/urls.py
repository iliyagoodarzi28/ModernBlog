from django.urls import path
from .views import ContactView
from django.views.generic import TemplateView

app_name = 'contact'

urlpatterns = [
    path('', ContactView.as_view(), name='contact'),
    path('success/', TemplateView.as_view(template_name='contact/success.html'), name='success'),
]
