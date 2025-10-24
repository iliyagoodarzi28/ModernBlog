from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .forms import ContactForm, NewsletterForm
from .models import Newsletter

class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:success')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        # Handle newsletter signup from footer
        if request.POST.get('newsletter_signup'):
            email = request.POST.get('email')
            if email:
                # For now, just show a success message
                # In a real application, you'd save this to a newsletter model
                messages.success(request, f'Thank you! We\'ve added {email} to our newsletter list.')
                return redirect('main:home')  # Redirect to home page
            else:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('main:home')
        
        # Handle regular contact form
        return super().post(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class NewsletterView(FormView):
    form_class = NewsletterForm
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        # Check if email already exists
        if Newsletter.objects.filter(email=email).exists():
            messages.info(self.request, 'This email is already subscribed to our newsletter.')
        else:
            form.save()
            messages.success(self.request, f'Thank you! We\'ve added {email} to our newsletter list.')
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please enter a valid email address.')
        return super().form_invalid(form)


@csrf_exempt
@require_POST
def newsletter_ajax(request):
    """AJAX endpoint for newsletter subscription"""
    email = request.POST.get('email')
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required'})
    
    try:
        # Check if email already exists
        if Newsletter.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'This email is already subscribed'})
        
        # Create new subscription
        Newsletter.objects.create(email=email)
        return JsonResponse({'success': True, 'message': 'Successfully subscribed to newsletter!'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
