from django.db import models
from markdownx.models import MarkdownxField
from .managers import ActiveManager , DeletedManager
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from .utils import blog_comment_info 




class BaseModel(models.Model):
    title = models.CharField(max_length=225 , verbose_name="Title")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    img = models.ImageField(upload_to='uploads/%Y/%m/%d',blank=True,verbose_name="Image")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    objects = models.Manager()
    active_objects = ActiveManager()
    delete_objects = DeletedManager()
    
    class Meta:
        abstract = True
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)    

    

class Category(BaseModel):
    """
    Base Model

    """
    class Meta(BaseModel.Meta):
        verbose_name = 'Categories'
        verbose_name_plural = "Categories"


    




class Blog(BaseModel):
    """
    Blog Model
    
    """
    category = models.ForeignKey(
        Category,on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name="Category"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name="Author",
        null=True,
        blank=True
    )
    description = MarkdownxField(verbose_name="Content")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Excerpt")
    views = models.PositiveIntegerField(default=0, verbose_name='Views')
    featured = models.BooleanField(default=False, verbose_name="Featured Post")
    reading_time = models.PositiveIntegerField(default=0, verbose_name="Reading Time (minutes)")

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
    
    def get_excerpt(self):
        if self.excerpt:
            return self.excerpt
        return self.description[:200] + "..." if len(self.description) > 200 else self.description

    class Meta(BaseModel.Meta):
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['featured', '-created_at']),
        ]







class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='User'
    )
    blog = models.ForeignKey(
        'Blog', 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='Blog'
    )
    content = models.TextField(verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    # Optional cache fields for faster template rendering
    name = models.CharField(max_length=255, blank=True, verbose_name='Name')
    email = models.EmailField(blank=True, verbose_name='Email')

    def save(self, *args, **kwargs):
        blog_comment_info(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.name or self.user} on {self.blog}"

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

