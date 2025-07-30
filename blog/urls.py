from django.urls import path
from . import views

app_name = 'blog'


urlpatterns = [
    path('',views.BlogListView.as_view(), name='blog_list'),
    path('detail/<slug:slug>/',views.BlogDetailView.as_view(),name='detail'),
    path('categories/',views.CategoryListView.as_view(),name='categories'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('blog/<slug:slug>/comment/', views.CommentCreateView.as_view(), name='comment_create'),



]