from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db.models import Count, Q
from markdownx.models import MarkdownxField
from .managers import ActiveManager, DeletedManager
from .utils import blog_comment_info 




class BaseModel(models.Model):
    """
    Abstract base model providing common fields and functionality
    for all content models in the blog application.
    """
    title = models.CharField(
        max_length=255, 
        verbose_name="Title",
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
        help_text="Enter a descriptive title (3-255 characters)"
    )
    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        blank=True, 
        verbose_name="Slug",
        help_text="URL-friendly version of the title (auto-generated)"
    )
    img = models.ImageField(
        upload_to='uploads/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name="Featured Image",
        help_text="Upload a high-quality image for better engagement"
    )
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        verbose_name="Meta Description",
        help_text="Brief description for search engines (max 160 characters)"
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Meta Keywords",
        help_text="Comma-separated keywords for SEO"
    )
    is_deleted = models.BooleanField(
        default=False, 
        verbose_name="Is Deleted",
        help_text="Soft delete flag"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Is Active",
        help_text="Whether this content is visible to users"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Updated At"
    )

    objects = models.Manager()
    active_objects = ActiveManager()
    delete_objects = DeletedManager()
    
    class Meta:
        abstract = True
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)    
    
    def get_absolute_url(self):
        """Override in child classes to provide URL routing"""
        raise NotImplementedError("Child classes must implement get_absolute_url")    

    

class Category(BaseModel):
    """
    Category model for organizing blog posts into topics.
    Provides hierarchical organization and SEO-friendly URLs.
    """
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Brief description of this category"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Parent Category",
        help_text="Optional parent category for hierarchical organization"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Sort Order",
        help_text="Order in which categories appear (lower numbers first)"
    )
    
    class Meta(BaseModel.Meta):
        verbose_name = 'Category'
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'title']
        indexes = [
            models.Index(fields=['parent', 'sort_order']),
            models.Index(fields=['is_active', 'sort_order']),
        ]

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})
    
    def get_blog_count(self):
        """Get count of active blogs in this category"""
        return self.blogs.filter(is_active=True).count()
    
    def get_total_views(self):
        """Get total views for all blogs in this category"""
        return self.blogs.filter(is_active=True).aggregate(
            total_views=models.Sum('views')
        )['total_views'] or 0


    




class Blog(BaseModel):
    """
    Blog post model with comprehensive content management features.
    Supports markdown content, SEO optimization, and social engagement.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name="Category",
        help_text="Select the most appropriate category"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name="Author",
        help_text="The author of this blog post",
        null=True,
        blank=True
    )
    description = MarkdownxField(
        verbose_name="Content",
        help_text="Write your blog post content using Markdown"
    )
    excerpt = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name="Excerpt",
        help_text="Brief summary for previews (auto-generated if empty)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Status",
        help_text="Publication status of the blog post"
    )
    views = models.PositiveIntegerField(
        default=0, 
        verbose_name='Views',
        help_text="Number of times this post has been viewed"
    )
    featured = models.BooleanField(
        default=False, 
        verbose_name="Featured Post",
        help_text="Mark as featured to highlight on homepage"
    )
    reading_time = models.PositiveIntegerField(
        default=0, 
        verbose_name="Reading Time (minutes)",
        help_text="Estimated reading time in minutes"
    )
    tags = models.ManyToManyField(
        'Tag', 
        blank=True, 
        related_name='blogs', 
        verbose_name="Tags",
        help_text="Add relevant tags for better discoverability"
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Published At",
        help_text="When this post was published"
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_blogs',
        verbose_name="Last Modified By"
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['featured', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['published_at']),
        ]

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count atomically"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_excerpt(self):
        """Get excerpt or generate from content"""
        if self.excerpt:
            return self.excerpt
        # Remove markdown formatting for excerpt
        import re
        content = re.sub(r'[#*`]', '', self.description)
        return content[:200] + "..." if len(content) > 200 else content
    
    def calculate_reading_time(self):
        """Calculate estimated reading time based on word count"""
        import re
        # Remove markdown formatting
        content = re.sub(r'[#*`\[\]()]', '', self.description)
        word_count = len(content.split())
        # Average reading speed: 200 words per minute
        return max(1, round(word_count / 200))
    
    def save(self, *args, **kwargs):
        # Auto-calculate reading time
        if not self.reading_time:
            self.reading_time = self.calculate_reading_time()
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_like_count(self):
        """Get total number of likes"""
        return self.likes.count()
    
    def get_comment_count(self):
        """Get total number of comments"""
        return self.comments.count()
    
    def is_published(self):
        """Check if blog is published and active"""
        return self.status == 'published' and self.is_active
    
    def get_related_posts(self, limit=3):
        """Get related posts from the same category"""
        return Blog.active_objects.filter(
            category=self.category,
            status='published'
        ).exclude(id=self.id)[:limit]







class Comment(models.Model):
    """
    Comment model for blog post discussions.
    Supports threaded comments and moderation features.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Spam'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='User',
        help_text="The user who wrote this comment"
    )
    blog = models.ForeignKey(
        'Blog', 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='Blog Post',
        help_text="The blog post this comment belongs to"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Parent Comment',
        help_text="For threaded comments"
    )
    content = models.TextField(
        verbose_name='Content',
        validators=[MinLengthValidator(10), MaxLengthValidator(1000)],
        help_text="Your comment (10-1000 characters)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='approved',
        verbose_name='Status',
        help_text="Moderation status of the comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    edited = models.BooleanField(
        default=False,
        verbose_name='Edited',
        help_text="Whether this comment has been edited"
    )

    # Optional cache fields for faster template rendering
    name = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Display Name',
        help_text="Cached display name"
    )
    email = models.EmailField(
        blank=True, 
        verbose_name='Email',
        help_text="Cached email address"
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blog', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['parent']),
        ]

    def save(self, *args, **kwargs):
        # Cache user information for performance
        blog_comment_info(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.name or self.user} on {self.blog.title}"
    
    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.filter(status='approved').order_by('created_at')
    
    def is_reply(self):
        """Check if this is a reply to another comment"""
        return self.parent is not None
    
    def get_depth(self):
        """Get the depth level of this comment in the thread"""
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
            if depth > 5:  # Prevent infinite loops
                break
        return depth


class Like(models.Model):
    """
    Like model for blog post engagement.
    Tracks user likes with timestamps for analytics.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='User',
        help_text="The user who liked this post"
    )
    blog = models.ForeignKey(
        'Blog',
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Blog Post',
        help_text="The blog post that was liked"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Created At'
    )

    class Meta:
        unique_together = ('user', 'blog')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blog', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.blog.title}"


class Bookmark(models.Model):
    """
    Bookmark model for saving blog posts.
    Allows users to save posts for later reading.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='User',
        help_text="The user who bookmarked this post"
    )
    blog = models.ForeignKey(
        'Blog',
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Blog Post',
        help_text="The blog post that was bookmarked"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Created At'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text="Personal notes about this bookmark"
    )

    class Meta:
        unique_together = ('user', 'blog')
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['blog', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.blog.title}"


class Tag(models.Model):
    """
    Tag model for categorizing blog posts.
    Provides flexible tagging system with usage statistics.
    """
    name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Tag Name',
        validators=[MinLengthValidator(2), MaxLengthValidator(50)],
        help_text="Tag name (2-50 characters)"
    )
    slug = models.SlugField(
        max_length=50, 
        unique=True, 
        blank=True, 
        verbose_name='Slug',
        help_text="URL-friendly version of the tag name"
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text="Brief description of this tag"
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Color',
        help_text="Hex color code for tag display"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Created At'
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Usage Count',
        help_text="Number of times this tag has been used"
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-usage_count']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})
    
    def update_usage_count(self):
        """Update the usage count for this tag"""
        self.usage_count = self.blogs.filter(is_active=True).count()
        self.save(update_fields=['usage_count'])
    
    def get_popular_posts(self, limit=5):
        """Get popular posts with this tag"""
        return self.blogs.filter(
            is_active=True,
            status='published'
        ).order_by('-views', '-created_at')[:limit]
