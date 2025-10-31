
from django.db.models import Q, Count
from django.db import models
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import re


def filter_and_sort_blogs(queryset, request):
    """
    Enhanced filtering and sorting for blog posts with advanced search capabilities.
    """
    query = request.GET.get('q', '').strip()
    if query:
        # Enhanced search across multiple fields
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(category__title__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__full_name__icontains=query) |
            Q(meta_keywords__icontains=query)
        ).distinct()

    # Filter by category
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category__slug=category)

    # Filter by tag
    tag = request.GET.get('tag')
    if tag:
        queryset = queryset.filter(tags__slug=tag)

    # Filter by author
    author = request.GET.get('author')
    if author:
        queryset = queryset.filter(author__username=author)

    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            queryset = queryset.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            queryset = queryset.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    # Filter by reading time
    reading_time_min = request.GET.get('reading_time_min')
    reading_time_max = request.GET.get('reading_time_max')
    
    if reading_time_min:
        try:
            queryset = queryset.filter(reading_time__gte=int(reading_time_min))
        except ValueError:
            pass
    
    if reading_time_max:
        try:
            queryset = queryset.filter(reading_time__lte=int(reading_time_max))
        except ValueError:
            pass

    # Enhanced sorting options
    sort_by = request.GET.get('sort')
    if sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
    elif sort_by == 'oldest':
        queryset = queryset.order_by('created_at')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-views')
    elif sort_by == 'trending':
        # Order by likes count and recent views
        queryset = queryset.annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-views')
    elif sort_by == 'reading_time':
        queryset = queryset.order_by('-reading_time')
    elif sort_by == 'alphabetical':
        queryset = queryset.order_by('title')
    else:
        queryset = queryset.order_by('-created_at')

    return queryset


def get_reading_time(content):
    """
    Calculate estimated reading time based on word count.
    """
    if not content:
        return 0
    
    # Remove markdown formatting
    content = re.sub(r'[#*`\[\]()]', '', content)
    word_count = len(content.split())
    
    # Average reading speed: 200 words per minute
    reading_time = max(1, round(word_count / 200))
    return reading_time


def blog_comment_info(comment):
    """
    Enhanced comment info caching with better user data handling.
    """
    name = comment.name
    email = comment.email

    if comment.user:
        if not name:
            name = getattr(comment.user, 'full_name', '') or getattr(comment.user, 'username', '')
        if not email:
            email = getattr(comment.user, 'email', '')

    return {
        'name': name,
        'email': email
    }


def get_popular_tags(limit=10):
    """
    Get most popular tags based on usage.
    """
    from .models import Tag
    return Tag.objects.annotate(
        usage_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
    ).filter(usage_count__gt=0).order_by('-usage_count')[:limit]


def get_trending_posts(limit=5, days=7):
    """
    Get trending posts based on recent activity.
    """
    from .models import Blog
    cutoff_date = timezone.now() - timedelta(days=days)
    
    return Blog.active_objects.filter(
        status='published',
        created_at__gte=cutoff_date
    ).annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-like_count', '-comment_count', '-views')[:limit]


def get_related_posts(blog, limit=4):
    """
    Get related posts based on category and tags.
    """
    from .models import Blog
    
    # Get posts from same category
    category_posts = Blog.active_objects.filter(
        category=blog.category,
        status='published'
    ).exclude(id=blog.id)
    
    # Get posts with similar tags
    tag_posts = Blog.active_objects.filter(
        tags__in=blog.tags.all(),
        status='published'
    ).exclude(id=blog.id).distinct()
    
    # Combine and prioritize
    related = (category_posts | tag_posts).distinct().order_by('-views', '-created_at')[:limit]
    
    return related


def get_author_stats(author):
    """
    Get comprehensive statistics for an author.
    """
    from .models import Blog, Comment, Like
    
    stats = {
        'total_posts': Blog.active_objects.filter(author=author, status='published').count(),
        'total_views': Blog.active_objects.filter(author=author, status='published').aggregate(
            total=models.Sum('views')
        )['total'] or 0,
        'total_likes': Like.objects.filter(blog__author=author).count(),
        'total_comments': Comment.objects.filter(blog__author=author).count(),
        'avg_reading_time': Blog.active_objects.filter(
            author=author, 
            status='published'
        ).aggregate(
            avg=models.Avg('reading_time')
        )['avg'] or 0,
    }
    
    return stats


def generate_sitemap_data():
    """
    Generate sitemap data for SEO.
    """
    from .models import Blog, Category, Tag
    
    sitemap_data = []
    
    # Add blog posts
    blogs = Blog.active_objects.filter(status='published').select_related('category')
    for blog in blogs:
        sitemap_data.append({
            'url': blog.get_absolute_url(),
            'lastmod': blog.updated_at,
            'changefreq': 'weekly',
            'priority': 0.8 if blog.featured else 0.6
        })
    
    # Add categories
    categories = Category.active_objects.all()
    for category in categories:
        sitemap_data.append({
            'url': category.get_absolute_url(),
            'lastmod': category.updated_at,
            'changefreq': 'monthly',
            'priority': 0.5
        })
    
    # Add tags
    tags = Tag.objects.all()
    for tag in tags:
        sitemap_data.append({
            'url': tag.get_absolute_url(),
            'lastmod': tag.created_at,
            'changefreq': 'monthly',
            'priority': 0.4
        })
    
    return sitemap_data


def clean_markdown_content(content):
    """
    Clean and sanitize markdown content.
    """
    if not content:
        return ""
    
    # Remove potentially harmful HTML tags
    import bleach
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                   'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img']
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height']
    }
    
    cleaned = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes)
    return cleaned


def extract_meta_description(content, max_length=160):
    """
    Extract or generate meta description from content.
    """
    if not content:
        return ""
    
    # Remove markdown formatting
    content = re.sub(r'[#*`\[\]()]', '', content)
    
    # Take first paragraph or first sentences
    sentences = content.split('.')
    description = ""
    
    for sentence in sentences:
        if len(description + sentence + '.') <= max_length:
            description += sentence + '.'
        else:
            break
    
    # If still too long, truncate
    if len(description) > max_length:
        description = description[:max_length-3] + '...'
    
    return description.strip()


def get_content_statistics():
    """
    Get overall content statistics for dashboard.
    """
    from .models import Blog, Category, Tag, Comment
    
    stats = {
        'total_posts': Blog.active_objects.filter(status='published').count(),
        'total_categories': Category.active_objects.count(),
        'total_tags': Tag.objects.count(),
        'total_comments': Comment.objects.filter(status='approved').count(),
        'total_views': Blog.active_objects.filter(status='published').aggregate(
            total=models.Sum('views')
        )['total'] or 0,
        'draft_posts': Blog.active_objects.filter(status='draft').count(),
        'featured_posts': Blog.active_objects.filter(featured=True, status='published').count(),
    }
    
    return stats