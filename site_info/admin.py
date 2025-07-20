from django.contrib import admin
from .models import SiteInfo

@admin.register(SiteInfo)
class SiteInfo(admin.ModelAdmin):
    list_display = ('name' , 'phone' , 'email' , 'created_at')
