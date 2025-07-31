
from django.db.models import Q

def filter_and_sort_blogs(queryset, request):
    query = request.GET.get('q', '').strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    sort_by = request.GET.get('sort')
    if sort_by == 'new':
        queryset = queryset.order_by('-date')
    elif sort_by == 'old':
        queryset = queryset.order_by('date')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-views')
    else:
        queryset = queryset.order_by('-date')

    return queryset



def blog_comment_info(comment):
    """
    Ensures the comment object has name and email fields populated from the user if missing.
    Returns a dictionary with name and email for display or further use.
    """
    name = comment.name
    email = comment.email

    if comment.user:
        if not name:
            name = getattr(comment.user, 'full_name', '') or getattr(comment.user, 'username', '')
        if not email:
            email = getattr(comment.user, 'email', '')

    return {
        'name': name,
        'email': email
    }