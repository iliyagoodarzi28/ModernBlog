from django.db import models
from markdownx.models import MarkdownxField
from .managers import ActiveManager , DeletedManager
from django.db import models
from django.conf import settings
from django.urls import reverse
from .utils import blog_comment_info 




class BaseModel(models.Model):
    title = models.CharField(max_length=225 , verbose_name="Title")
    slug = models.SlugField(default="", null=False , verbose_name="Slug")
    img = models.ImageField(upload_to='uploads/%Y/%m/%d',blank=True,verbose_name="Image")
    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")


    objects = models.Manager()
    active_objects = ActiveManager()
    delete_objects = DeletedManager()
    

    class Meta:
        abstract = True
        ordering = ('title',)

    def __str__(self):
        return self.title    

    

class Category(BaseModel):
    """
    Base Model

    """
    class Meta(BaseModel.Meta):
        verbose_name = 'Categories'
        verbose_name_plural = "Categories"


    




class Blog(BaseModel):
    """
    Base Model
    
    """
    category = models.ForeignKey(
        Category,on_delete=models.CASCADE,
        related_name='Blogs',
        verbose_name="Category"
    )
    description = MarkdownxField()
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    views = models.PositiveIntegerField(default=0, verbose_name='Views')


    def increment_views(self):
        self.views += 1
        self.save()

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
    


    class Meta(BaseModel.Meta):
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'







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

