from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from blog.models import Blog, Category

User = get_user_model()


class MainView(TemplateView):
    template_name = 'main/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured posts (posts marked as featured)
        context['featured_blogs'] = Blog.active_objects.filter(featured=True)[:3]
        
        # Get latest posts
        context['latest_blogs'] = Blog.active_objects.all()[:6]
        
        # Get all categories
        context['categories'] = Category.active_objects.all()[:8]
        
        # Get statistics
        context['total_posts'] = Blog.active_objects.count()
        context['total_categories'] = Category.active_objects.count()
        context['total_views'] = sum(blog.views for blog in Blog.active_objects.all())
        context['total_users'] = User.objects.count()
        
        return context


class AboutView(TemplateView):
    template_name = 'main/about.html'
