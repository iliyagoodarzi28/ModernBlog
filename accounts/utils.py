from datetime import date
from django.utils.translation import gettext_lazy as _


def calculate_age(birth_date):
    """محاسبه سن بر اساس تاریخ تولد"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def get_user_stats(user):
    """Get comprehensive user statistics"""
    from blog.models import Blog, Like, Bookmark, Comment
    
    stats = {
        'posts_count': Blog.objects.filter(author=user, is_active=True).count(),
        'total_views': sum(Blog.objects.filter(author=user, is_active=True).values_list('views', flat=True)),
        'likes_received': Like.objects.filter(blog__author=user).count(),
        'bookmarks_received': Bookmark.objects.filter(blog__author=user).count(),
        'comments_count': Comment.objects.filter(user=user).count(),
        'followers_count': 0,  # Will be implemented with follow system
        'following_count': 0,  # Will be implemented with follow system
    }
    return stats


def get_recent_activities(user, limit=10):
    """Get recent user activities"""
    activities = []
    
    # Recent posts
    from blog.models import Blog
    recent_posts = Blog.objects.filter(author=user, is_active=True).order_by('-created_at')[:5]
    for post in recent_posts:
        activities.append({
            'type': 'post_created',
            'title': f'Created post: {post.title}',
            'description': f'Published a new blog post',
            'created_at': post.created_at,
            'icon': 'newspaper',
            'url': post.get_absolute_url()
        })
    
    # Recent comments
    from blog.models import Comment
    recent_comments = Comment.objects.filter(user=user).order_by('-created_at')[:5]
    for comment in recent_comments:
        activities.append({
            'type': 'comment_created',
            'title': f'Commented on: {comment.blog.title}',
            'description': f'Left a comment on a blog post',
            'created_at': comment.created_at,
            'icon': 'comment',
            'url': comment.blog.get_absolute_url()
        })
    
    # Sort by date and return limited results
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    return activities[:limit]


def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, _("Password must be at least 8 characters long")
    
    if not any(c.islower() for c in password):
        return False, _("Password must contain at least one lowercase letter")
    
    if not any(c.isupper() for c in password):
        return False, _("Password must contain at least one uppercase letter")
    
    if not any(c.isdigit() for c in password):
        return False, _("Password must contain at least one number")
    
    return True, _("Password is strong")


def get_password_strength_score(password):
    """Calculate password strength score (0-100)"""
    score = 0
    
    # Length
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    
    # Character variety
    if any(c.islower() for c in password):
        score += 10
    if any(c.isupper() for c in password):
        score += 10
    if any(c.isdigit() for c in password):
        score += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 20
    
    # Common patterns penalty
    common_patterns = ['123', 'abc', 'qwe', 'password', 'admin']
    if any(pattern in password.lower() for pattern in common_patterns):
        score -= 20
    
    return min(max(score, 0), 100)


GENDER_CHOICES = (
    ('male', _('Male')),
    ('female', _('Female')),
    ('other', _('Other')),
    ('prefer_not_to_say', _('Prefer not to say')),
)


ACCOUNT_STATUS_CHOICES = (
    ('active', _('Active')),
    ('inactive', _('Inactive')),
    ('suspended', _('Suspended')),
    ('pending', _('Pending Verification')),
)


def format_user_name(user):
    """Format user name for display"""
    if user.full_name:
        return user.full_name
    return f"@{user.username}"


def get_user_initial(user):
    """Get user's initial for avatar placeholder"""
    if user.full_name:
        return user.full_name[0].upper()
    return user.username[0].upper() if user.username else "U"