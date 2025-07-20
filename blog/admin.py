from django.contrib import admin
from .models import Category, Blog
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    ordering = ('title',)

@admin.register(Blog)
class BlogAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'category', 'date', 'slug')
    list_filter = ('category', 'date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    ordering = ('-date',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'img', 'description')
        }),
    )
