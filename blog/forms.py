from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import Comment, Blog, Category, Tag


class CommentForm(forms.ModelForm):
    """
    Enhanced comment form with better validation and user experience.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your thoughts...',
            'rows': 4,
            'maxlength': 1000
        }),
        validators=[MinLengthValidator(10), MaxLengthValidator(1000)],
        help_text="Minimum 10 characters, maximum 1000 characters"
    )
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def clean_content(self):
        """Clean and validate comment content"""
        content = self.cleaned_data.get('content', '').strip()
        
        if not content:
            raise ValidationError("Comment cannot be empty.")
        
        # Remove HTML tags for security
        content = strip_tags(content)
        
        if len(content) < 10:
            raise ValidationError("Comment must be at least 10 characters long.")
        
        if len(content) > 1000:
            raise ValidationError("Comment cannot exceed 1000 characters.")
        
        return content


class BlogCreateForm(forms.ModelForm):
    """
    Enhanced blog creation form with rich editor and validation.
    """
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter an engaging title...',
            'maxlength': 255
        }),
        validators=[MinLengthValidator(10), MaxLengthValidator(255)],
        help_text="Make it catchy and descriptive (10-255 characters)"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.active_objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        empty_label="Select a category",
        help_text="Choose the most appropriate category"
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 20,
            'placeholder': 'Write your blog post content here...',
            'data-provide': 'markdown-editor'
        }),
        help_text="Use Markdown for formatting. Minimum 100 characters."
    )
    
    excerpt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief summary (optional - will be auto-generated if empty)',
            'maxlength': 500
        }),
        validators=[MaxLengthValidator(500)],
        help_text="Optional brief summary (max 500 characters)"
    )
    
    img = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload a high-quality featured image (recommended: 1200x630px)"
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 8
        }),
        required=False,
        help_text="Select relevant tags (hold Ctrl/Cmd to select multiple)"
    )
    
    featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Mark as featured to highlight on homepage"
    )
    
    status = forms.ChoiceField(
        choices=Blog.STATUS_CHOICES,
        initial='draft',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text="Choose publication status"
    )
    
    class Meta:
        model = Blog
        fields = [
            'title', 'category', 'description', 'excerpt', 
            'img', 'tags', 'featured', 'status', 'meta_description', 'meta_keywords'
        ]
        widgets = {
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO description (max 160 characters)',
                'maxlength': 160
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO keywords (comma-separated)',
                'maxlength': 255
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.active_objects.all()
        self.fields['tags'].queryset = Tag.objects.all()
    
    def clean_title(self):
        """Validate and clean title"""
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise ValidationError("Title is required.")
        
        if len(title) < 10:
            raise ValidationError("Title must be at least 10 characters long.")
        
        return title
    
    def clean_description(self):
        """Validate blog content"""
        description = self.cleaned_data.get('description', '').strip()
        
        if not description:
            raise ValidationError("Blog content is required.")
        
        if len(description) < 100:
            raise ValidationError("Blog content must be at least 100 characters long.")
        
        return description
    
    def clean_excerpt(self):
        """Clean excerpt or generate from content"""
        excerpt = self.cleaned_data.get('excerpt', '').strip()
        
        if not excerpt and self.cleaned_data.get('description'):
            # Auto-generate excerpt from content
            content = self.cleaned_data['description']
            # Remove markdown formatting
            import re
            content = re.sub(r'[#*`\[\]()]', '', content)
            excerpt = content[:200] + "..." if len(content) > 200 else content
        
        return excerpt
    
    def clean_img(self):
        """Validate image upload"""
        img = self.cleaned_data.get('img')
        
        if img:
            # Check file size (max 5MB)
            if img.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size cannot exceed 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if img.content_type not in allowed_types:
                raise ValidationError("Only JPEG, PNG, GIF, and WebP images are allowed.")
        
        return img


class BlogUpdateForm(BlogCreateForm):
    """
    Blog update form with additional fields for modification tracking.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add update reason field for tracking changes
        self.fields['update_reason'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for update (optional)',
                'maxlength': 200
            }),
            help_text="Optional note about what was changed"
        )


class CommentReplyForm(forms.ModelForm):
    """
    Form for replying to comments with threading support.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your reply...',
            'rows': 3,
            'maxlength': 1000
        }),
        validators=[MinLengthValidator(10), MaxLengthValidator(1000)]
    )
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def clean_content(self):
        """Clean reply content"""
        content = self.cleaned_data.get('content', '').strip()
        
        if not content:
            raise ValidationError("Reply cannot be empty.")
        
        content = strip_tags(content)
        
        if len(content) < 10:
            raise ValidationError("Reply must be at least 10 characters long.")
        
        return content


class BlogSearchForm(forms.Form):
    """
    Advanced search form for blog posts.
    """
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...',
            'maxlength': 100
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.active_objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 5
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('', 'Sort by'),
            ('newest', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('popular', 'Most Popular'),
            ('trending', 'Trending'),
            ('reading_time', 'Reading Time')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )