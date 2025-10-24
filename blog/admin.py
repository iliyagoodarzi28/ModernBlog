from django.contrib import admin
from .models import Category, Blog, Comment
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'is_deleted', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'meta_description')
    ordering = ('-created_at',)
    list_filter = ('is_active', 'is_deleted', 'created_at')
    list_editable = ('is_active', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'img', 'meta_description', 'meta_keywords')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Blog)
class BlogAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'views', 'featured', 'is_active', 'is_deleted')
    list_filter = ('category', 'author', 'created_at', 'featured', 'is_active', 'is_deleted')
    search_fields = ('title', 'description', 'excerpt', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('views', 'created_at', 'updated_at', 'reading_time')
    list_editable = ('featured', 'is_active', 'is_deleted')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'img', 'description', 'excerpt')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('featured', 'is_active', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'blog', 'created_at', 'user')
    list_filter = ('created_at', 'blog', 'user')
    search_fields = ('name', 'email', 'content', 'blog__title')
    readonly_fields = ('created_at', 'user', 'name', 'email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'blog', 'content')
        }),
        ('User Information', {
            'fields': ('name', 'email'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'blog')
    
