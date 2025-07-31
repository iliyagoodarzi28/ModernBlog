from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class AuthenticatedAccessMixin(LoginRequiredMixin):
    login_url = reverse_lazy('accounts:login')
    redirect_field_name = 'next'

