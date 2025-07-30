from django.contrib import admin
from .models import Category, Blog, Comment
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'is_deleted')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    ordering = ('title',)
    list_filter = ('is_active', 'is_deleted')
    list_editable = ('is_active', 'is_deleted')

@admin.register(Blog)
class BlogAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'category', 'date', 'slug', 'views', 'is_active', 'is_deleted')
    list_filter = ('category', 'date', 'is_active', 'is_deleted')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('views',)
    list_editable = ('is_active', 'is_deleted')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'img', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )

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
    
