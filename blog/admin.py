from django.contrib import admin
from .models import Category, Blog
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'is_deleted')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    ordering = ('title',)
    list_filter = ('is_active', 'is_deleted')

@admin.register(Blog)
class BlogAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'category', 'date', 'slug', 'views', 'is_active', 'is_deleted')
    list_filter = ('category', 'date', 'is_active', 'is_deleted')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('views',)

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
    
