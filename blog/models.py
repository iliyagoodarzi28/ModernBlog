from django.db import models
from markdownx.models import MarkdownxField


class BaseModel(models.Model):
    title = models.CharField(max_length=225 , verbose_name="Title")
    slug = models.SlugField(default="", null=False , verbose_name="Slug")
    img = models.ImageField(upload_to='uploads/%Y/%m/%d',blank=True,verbose_name="Image")

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

    class Meta(BaseModel.Meta):
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
