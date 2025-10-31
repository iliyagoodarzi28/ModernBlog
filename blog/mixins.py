from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib import messages


class AuthorRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure only the author can access their own blog posts.
    """
    
    def test_func(self):
        """Test if user is the author of the blog post"""
        if not self.request.user.is_authenticated:
            return False
        
        # For detail views, check if user is author
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            return obj.author == self.request.user
        
        # For list views, filter queryset
        return True
    
    def get_queryset(self):
        """Filter queryset to only show user's own posts"""
        if hasattr(super(), 'get_queryset'):
            queryset = super().get_queryset()
            return queryset.filter(author=self.request.user)
        return super().get_queryset()
    
    def handle_no_permission(self):
        """Handle permission denied"""
        messages.error(self.request, "You don't have permission to access this content.")
        return super().handle_no_permission()


class SearchAndSortContextMixin:
    """
    Mixin to provide search and sort context to templates.
    """
    
    def get_context_data(self, **kwargs):
        """Add search and sort context"""
        context = super().get_context_data(**kwargs)
        
        # Search context
        context['search_query'] = self.request.GET.get('q', '')
        context['search_form'] = self.get_search_form()
        
        # Sort context
        context['sort_options'] = self.get_sort_options()
        context['current_sort'] = self.request.GET.get('sort', '')
        
        # Filter context
        context['filter_form'] = self.get_filter_form()
        
        return context
    
    def get_search_form(self):
        """Get search form instance"""
        from .forms import BlogSearchForm
        return BlogSearchForm(self.request.GET)
    
    def get_sort_options(self):
        """Get available sort options"""
        return [
            ('', 'Sort by'),
            ('newest', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('popular', 'Most Popular'),
            ('trending', 'Trending'),
            ('reading_time', 'Reading Time'),
            ('alphabetical', 'A-Z')
        ]
    
    def get_filter_form(self):
        """Get filter form instance"""
        from .forms import BlogSearchForm
        return BlogSearchForm(self.request.GET)


class PaginationMixin:
    """
    Mixin to provide enhanced pagination functionality.
    """
    paginate_by = 12
    paginate_orphans = 3
    
    def get_paginate_by(self, queryset):
        """Get pagination size from request or default"""
        return self.request.GET.get('per_page', self.paginate_by)
    
    def get_context_data(self, **kwargs):
        """Add pagination context"""
        context = super().get_context_data(**kwargs)
        
        if 'page_obj' in context:
            page_obj = context['page_obj']
            
            # Add pagination info
            context['pagination_info'] = {
                'current_page': page_obj.number,
                'total_pages': page_obj.paginator.num_pages,
                'total_items': page_obj.paginator.count,
                'items_per_page': page_obj.paginator.per_page,
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index(),
            }
            
            # Add page range for pagination
            context['page_range'] = self.get_page_range(page_obj)
        
        return context
    
    def get_page_range(self, page_obj):
        """Get page range for pagination display"""
        current_page = page_obj.number
        total_pages = page_obj.paginator.num_pages
        
        # Show 5 pages around current page
        start = max(1, current_page - 2)
        end = min(total_pages, current_page + 2)
        
        return range(start, end + 1)


class CacheControlMixin:
    """
    Mixin to add cache control headers.
    """
    cache_timeout = 300  # 5 minutes
    
    def dispatch(self, request, *args, **kwargs):
        """Add cache headers"""
        response = super().dispatch(request, *args, **kwargs)
        
        # Add cache headers for GET requests
        if request.method == 'GET':
            response['Cache-Control'] = f'public, max-age={self.cache_timeout}'
        
        return response


class SEOContextMixin:
    """
    Mixin to provide SEO context for templates.
    """
    
    def get_context_data(self, **kwargs):
        """Add SEO context"""
        context = super().get_context_data(**kwargs)
        
        # Default SEO values
        context['seo_title'] = getattr(self, 'seo_title', '')
        context['seo_description'] = getattr(self, 'seo_description', '')
        context['seo_keywords'] = getattr(self, 'seo_keywords', '')
        context['seo_image'] = getattr(self, 'seo_image', '')
        
        return context


class AnalyticsMixin:
    """
    Mixin to provide analytics tracking.
    """
    
    def get_context_data(self, **kwargs):
        """Add analytics context"""
        context = super().get_context_data(**kwargs)
        
        # Add analytics tracking
        context['track_page_view'] = True
        context['page_category'] = getattr(self, 'page_category', 'blog')
        
        return context


class SocialSharingMixin:
    """
    Mixin to provide social sharing context.
    """
    
    def get_context_data(self, **kwargs):
        """Add social sharing context"""
        context = super().get_context_data(**kwargs)
        
        # Get object for sharing
        obj = getattr(self, 'object', None)
        
        if obj:
            context['share_url'] = self.request.build_absolute_uri(obj.get_absolute_url())
            context['share_title'] = getattr(obj, 'title', '')
            context['share_description'] = getattr(obj, 'get_excerpt', lambda: '')()
            context['share_image'] = getattr(obj, 'img', None)
        
        return context