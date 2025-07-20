from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import ContactForm

class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:success')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
