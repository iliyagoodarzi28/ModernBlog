from django.urls import path
from . import views

app_name = 'blog'


urlpatterns = [
    # Blog listing and search
    path('', views.BlogListView.as_view(), name='list'),
    path('search/', views.BlogListView.as_view(), name='search'),
    
    # Blog detail and management
    path('detail/<slug:slug>/', views.BlogDetailView.as_view(), name='detail'),
    path('create/', views.BlogCreateView.as_view(), name='create'),
    path('update/<slug:slug>/', views.BlogUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>/', views.BlogDeleteView.as_view(), name='delete'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Tags
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # Comments and interactions
    path('blog/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Social interactions
    path('blog/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
    path('blog/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('blog/<slug:slug>/bookmark/notes/', views.update_bookmark_notes, name='update_bookmark_notes'),
]