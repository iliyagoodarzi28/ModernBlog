from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.safestring import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone
import markdown

from .models import Blog, Category, Comment, Like, Bookmark, Tag
from .forms import CommentForm, BlogCreateForm, BlogUpdateForm
from .utils import filter_and_sort_blogs, get_reading_time
from .mixins import SearchAndSortContextMixin, AuthorRequiredMixin
from accounts.mixins import AuthenticatedAccessMixin



class BlogListView(SearchAndSortContextMixin, ListView):
    """
    Enhanced blog list view with advanced filtering, sorting, and pagination.
    Provides comprehensive search functionality and performance optimizations.
    """
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 12
    paginate_orphans = 3
    ordering = ['-created_at']

    def get_queryset(self):
        """Get optimized queryset with prefetching and filtering"""
        queryset = Blog.active_objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'likes', 'comments'
        ).annotate(
            like_count=Count('likes'),
            comment_count=Count('comments'),
            is_liked_by_user=Count(
                'likes',
                filter=Q(likes__user=self.request.user) if self.request.user.is_authenticated else Q()
            )
        )
        
        # Apply filtering and sorting
        queryset = filter_and_sort_blogs(queryset, self.request)
        
        # Only show published posts for non-authors
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset

    def get_context_data(self, **kwargs):
        """Add additional context for enhanced functionality"""
        context = super().get_context_data(**kwargs)
        
        # Categories with blog counts
        context['categories'] = Category.active_objects.annotate(
            blog_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
        ).filter(blog_count__gt=0).order_by('-blog_count', 'title')
        
        # Popular blogs for sidebar
        context['popular_blogs'] = Blog.active_objects.filter(
            status='published'
        ).select_related('author', 'category').annotate(
            like_count=Count('likes')
        ).order_by('-views', '-like_count')[:6]
        
        # Recent tags
        context['recent_tags'] = Tag.objects.annotate(
            usage_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:10]
        
        # Featured posts
        context['featured_posts'] = Blog.active_objects.filter(
            featured=True,
            status='published'
        ).select_related('author', 'category')[:3]
        
        # Search and filter context
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        
        return context


        


class BlogDetailView(DetailView):
    """
    Enhanced blog detail view with comprehensive content display,
    social features, and related content recommendations.
    """
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Get blog with optimized queries"""
        return Blog.active_objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'likes', 'comments__user'
        ).annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        )

    def get_object(self, queryset=None):
        """Get blog object and increment view count"""
        obj = super().get_object(queryset)
        
        # Only increment views for published posts
        if obj.status == 'published':
            obj.increment_views()
        
        return obj

    def get_context_data(self, **kwargs):
        """Add comprehensive context for blog detail page"""
        context = super().get_context_data(**kwargs)
        blog = self.object
        
        # Convert markdown to HTML
        context['description_html'] = mark_safe(markdown.markdown(blog.description))
        
        # Comment form
        context['form'] = CommentForm()
        
        # User interaction status
        if self.request.user.is_authenticated:
            context['is_liked'] = Like.objects.filter(
                user=self.request.user, 
                blog=blog
            ).exists()
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user, 
                blog=blog
            ).exists()
        else:
            context['is_liked'] = False
            context['is_bookmarked'] = False
        
        # Related posts
        context['related_posts'] = blog.get_related_posts(limit=4)
        
        # Author's other posts
        context['author_posts'] = Blog.active_objects.filter(
            author=blog.author,
            status='published'
        ).exclude(id=blog.id)[:3]
        
        # Comments with replies
        context['comments'] = Comment.objects.filter(
            blog=blog,
            status='approved',
            parent=None
        ).select_related('user').prefetch_related('replies__user').order_by('-created_at')
        
        # Social sharing data
        context['share_url'] = self.request.build_absolute_uri(blog.get_absolute_url())
        context['share_title'] = blog.title
        context['share_description'] = blog.get_excerpt()
        
        return context


class CategoryListView(ListView):
    """
    Enhanced category list view with statistics and visual improvements.
    """
    model = Category
    template_name = 'category/categories.html'
    context_object_name = 'categories'
    paginate_by = 12
    ordering = ['sort_order', 'title']

    def get_queryset(self):
        """Get categories with blog statistics"""
        return Category.active_objects.annotate(
            blog_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published')),
            total_views=Count('blogs__views', filter=Q(blogs__is_active=True, blogs__status='published'))
        ).filter(blog_count__gt=0)

    def get_context_data(self, **kwargs):
        """Add statistics and popular categories"""
        context = super().get_context_data(**kwargs)
        
        # Overall statistics
        context['total_posts'] = Blog.active_objects.filter(status='published').count()
        context['total_views'] = Blog.active_objects.filter(status='published').aggregate(
            total=Count('views')
        )['total'] or 0
        
        # Popular categories
        context['popular_categories'] = Category.active_objects.annotate(
            total_views=Count('blogs__views', filter=Q(blogs__is_active=True, blogs__status='published'))
        ).order_by('-total_views')[:6]
        
        return context


class CategoryDetailView(DetailView):
    """
    Enhanced category detail view with blog listing and filtering.
    """
    model = Category
    template_name = 'category/category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    paginate_by = 12

    def get_queryset(self):
        """Get category with blog count"""
        return Category.active_objects.annotate(
            blog_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
        )

    def get_context_data(self, **kwargs):
        """Add blogs and related context"""
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Get blogs in this category
        blogs = Blog.active_objects.filter(
            category=category,
            status='published'
        ).select_related('author').prefetch_related('tags', 'likes').annotate(
            like_count=Count('likes')
        )
        
        # Apply filtering and sorting
        blogs = filter_and_sort_blogs(blogs, self.request)
        
        # Paginate blogs
        paginator = Paginator(blogs, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['blogs'] = paginator.get_page(page_number)
        
        # Related categories
        context['related_categories'] = Category.active_objects.exclude(
            id=category.id
        ).annotate(
            blog_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
        ).filter(blog_count__gt=0)[:4]
        
        return context


class TagDetailView(DetailView):
    """
    Tag detail view showing all posts with a specific tag.
    """
    model = Tag
    template_name = 'blog/tag_detail.html'
    context_object_name = 'tag'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """Add blogs with this tag"""
        context = super().get_context_data(**kwargs)
        tag = self.object
        
        # Get blogs with this tag
        blogs = Blog.active_objects.filter(
            tags=tag,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags', 'likes').annotate(
            like_count=Count('likes')
        )
        
        # Apply filtering and sorting
        blogs = filter_and_sort_blogs(blogs, self.request)
        
        # Paginate blogs
        paginator = Paginator(blogs, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['blogs'] = paginator.get_page(page_number)
        
        # Related tags
        context['related_tags'] = Tag.objects.annotate(
            usage_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
        ).filter(usage_count__gt=0).exclude(id=tag.id).order_by('-usage_count')[:8]
        
        return context


class CommentCreateView(AuthenticatedAccessMixin, CreateView):
    """
    Enhanced comment creation with threading support and moderation.
    """
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        """Set comment author and blog, handle threading"""
        form.instance.user = self.request.user
        form.instance.blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        
        # Handle reply to comment
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            form.instance.parent = parent_comment
        
        messages.success(self.request, 'Your comment has been posted!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to blog post with comment anchor"""
        return f"{self.object.blog.get_absolute_url()}#comment-{self.object.id}"


class BlogCreateView(AuthenticatedAccessMixin, CreateView):
    """
    Enhanced blog creation with rich editor and auto-save functionality.
    """
    model = Blog
    form_class = BlogCreateForm
    template_name = 'blog/blog_create.html'
    success_url = reverse_lazy('blog:list')

    def form_valid(self, form):
        """Set author and handle auto-publishing"""
        form.instance.author = self.request.user
        
        # Auto-calculate reading time
        if not form.instance.reading_time:
            form.instance.reading_time = get_reading_time(form.instance.description)
        
        # Set published_at if status is published
        if form.instance.status == 'published':
            form.instance.published_at = timezone.now()
        
        messages.success(self.request, 'Blog post created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add categories and tags for form"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.active_objects.all()
        context['tags'] = Tag.objects.all()
        return context


class BlogUpdateView(AuthorRequiredMixin, UpdateView):
    """
    Enhanced blog update with version control and change tracking.
    """
    model = Blog
    form_class = BlogUpdateForm
    template_name = 'blog/blog_update.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Only allow authors to edit their own posts"""
        return Blog.objects.filter(author=self.request.user)

    def form_valid(self, form):
        """Track modifications and update timestamps"""
        form.instance.last_modified_by = self.request.user
        
        # Recalculate reading time if content changed
        if 'description' in form.changed_data:
            form.instance.reading_time = get_reading_time(form.instance.description)
        
        # Update published_at if status changed to published
        if form.instance.status == 'published' and not form.instance.published_at:
            form.instance.published_at = timezone.now()
        
        messages.success(self.request, 'Blog post updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to updated blog post"""
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        """Add categories and tags for form"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.active_objects.all()
        context['tags'] = Tag.objects.all()
        return context


class BlogDeleteView(AuthorRequiredMixin, DeleteView):
    """
    Soft delete for blog posts with confirmation.
    """
    model = Blog
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:list')

    def get_queryset(self):
        """Only allow authors to delete their own posts"""
        return Blog.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Soft delete instead of hard delete"""
        self.object = self.get_object()
        self.object.is_deleted = True
        self.object.is_active = False
        self.object.save()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect(self.success_url)


# AJAX Views for Social Interactions

@require_POST
@login_required
def toggle_like(request, slug):
    """
    Toggle like for a blog post with enhanced response data.
    """
    blog = get_object_or_404(Blog, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, blog=blog)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    like_count = blog.likes.count()
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': 'Liked!' if liked else 'Like removed'
    })


@require_POST
@login_required
def toggle_bookmark(request, slug):
    """
    Toggle bookmark for a blog post with notes support.
    """
    blog = get_object_or_404(Blog, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, blog=blog)
    
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    
    return JsonResponse({
        'success': True,
        'bookmarked': bookmarked,
        'message': 'Bookmarked!' if bookmarked else 'Bookmark removed'
    })


@require_POST
@login_required
def delete_comment(request, comment_id):
    """
    Delete a comment with enhanced error handling.
    """
    try:
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Comment deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error deleting comment'
        }, status=500)


@require_POST
@login_required
def reply_to_comment(request, comment_id):
    """
    Create a reply to an existing comment.
    """
    try:
        parent_comment = get_object_or_404(Comment, id=comment_id)
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({
                'success': False,
                'message': 'Comment content is required'
            }, status=400)
        
        reply = Comment.objects.create(
            user=request.user,
            blog=parent_comment.blog,
            parent=parent_comment,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Reply posted successfully',
            'comment_id': reply.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error posting reply'
        }, status=500)


@require_POST
@login_required
def update_bookmark_notes(request, slug):
    """
    Update notes for a bookmarked post.
    """
    try:
        bookmark = get_object_or_404(Bookmark, user=request.user, blog__slug=slug)
        notes = request.POST.get('notes', '').strip()
        bookmark.notes = notes
        bookmark.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notes updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error updating notes'
        }, status=500)
