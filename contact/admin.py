from django.contrib import admin
from . models import ContactMessage, Newsletter

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name' , 'email' , 'subject' , 'created_at')
    search_fields = ('name' , 'email' , 'subject' , 'message')
    readonly_fields = ('name' , 'email' , 'subject' , 'message' , 'created_at')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    search_fields = ('email',)
    list_filter = ('is_active', 'subscribed_at')
    readonly_fields = ('subscribed_at',)