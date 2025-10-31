from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from .models import Category, Blog, Comment, Like, Bookmark, Tag
from markdownx.admin import MarkdownxModelAdmin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Enhanced category admin with better organization and statistics.
    """
    list_display = ('title', 'slug', 'blog_count', 'total_views', 'is_active', 'is_deleted', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description', 'meta_description')
    ordering = ('sort_order', 'title')
    list_filter = ('is_active', 'is_deleted', 'created_at', 'parent')
    list_editable = ('is_active', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at', 'blog_count', 'total_views')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'img', 'parent', 'sort_order')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('blog_count', 'total_views'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            blog_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published')),
            total_views=Sum('blogs__views', filter=Q(blogs__is_active=True, blogs__status='published'))
        )
    
    def blog_count(self, obj):
        return obj.blog_count or 0
    blog_count.short_description = 'Posts'
    
    def total_views(self, obj):
        return obj.total_views or 0
    total_views.short_description = 'Total Views'


@admin.register(Blog)
class BlogAdmin(MarkdownxModelAdmin):
    """
    Enhanced blog admin with comprehensive management features.
    """
    list_display = ('title', 'author', 'category', 'status', 'views', 'like_count', 'comment_count', 'featured', 'is_active', 'created_at')
    list_filter = ('category', 'author', 'status', 'featured', 'is_active', 'is_deleted', 'created_at', 'published_at')
    search_fields = ('title', 'description', 'excerpt', 'meta_description', 'author__username', 'author__full_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('views', 'reading_time', 'created_at', 'updated_at', 'published_at', 'like_count', 'comment_count')
    list_editable = ('featured', 'is_active', 'status')
    filter_horizontal = ('tags',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'status', 'img', 'description', 'excerpt')
        }),
        ('Content Organization', {
            'fields': ('tags', 'featured'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'reading_time', 'like_count', 'comment_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author').prefetch_related('tags').annotate(
            like_count=Count('likes'),
            comment_count=Count('comments')
        )
    
    def like_count(self, obj):
        return obj.like_count or 0
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        return obj.comment_count or 0
    comment_count.short_description = 'Comments'
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Enhanced comment admin with moderation features.
    """
    list_display = ('content_preview', 'user', 'blog_title', 'status', 'created_at', 'is_reply')
    list_filter = ('status', 'created_at', 'blog__category', 'parent')
    search_fields = ('content', 'user__username', 'user__full_name', 'blog__title')
    readonly_fields = ('created_at', 'updated_at', 'user', 'name', 'email', 'is_reply')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'blog', 'parent', 'content', 'status')
        }),
        ('User Information', {
            'fields': ('name', 'email'),
            'classes': ('collapse',)
        }),
        ('Comment Properties', {
            'fields': ('is_reply', 'depth', 'edited'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'blog', 'parent')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def blog_title(self, obj):
        return obj.blog.title
    blog_title.short_description = 'Blog Post'
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Like admin for monitoring user engagement.
    """
    list_display = ('user', 'blog_title', 'created_at')
    list_filter = ('created_at', 'blog__category')
    search_fields = ('user__username', 'user__full_name', 'blog__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'blog')
    
    def blog_title(self, obj):
        return obj.blog.title
    blog_title.short_description = 'Blog Post'


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """
    Bookmark admin for user content management.
    """
    list_display = ('user', 'blog_title', 'created_at', 'has_notes')
    list_filter = ('created_at', 'blog__category')
    search_fields = ('user__username', 'user__full_name', 'blog__title', 'notes')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'blog', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'blog')
    
    def blog_title(self, obj):
        return obj.blog.title
    blog_title.short_description = 'Blog Post'
    
    def has_notes(self, obj):
        return bool(obj.notes)
    has_notes.boolean = True
    has_notes.short_description = 'Has Notes'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Enhanced tag admin with usage statistics.
    """
    list_display = ('name', 'slug', 'usage_count', 'color_display', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'usage_count', 'color_display')
    list_editable = ('usage_count',)
    ordering = ('-usage_count', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'color')
        }),
        ('Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            usage_count=Count('blogs', filter=Q(blogs__is_active=True, blogs__status='published'))
        )
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def usage_count(self, obj):
        return obj.usage_count or 0
    usage_count.short_description = 'Usage Count'


# Custom admin site configuration
admin.site.site_header = "ModernBlog Administration"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Welcome to ModernBlog Administration"
