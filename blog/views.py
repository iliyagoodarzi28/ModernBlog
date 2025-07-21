from django.shortcuts import render
from django.views.generic import  ListView , DetailView
from . models import Blog , Category

import markdown
from django.utils.safestring import mark_safe



class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog.html'
    ordering = ['-date']
    page_kwarg = 'page'
    paginate_orphans = 3
    paginate_by = 9
    context_object_name = 'blogs'


    def get_queryset(self):
        return Blog.active_objects.all()




class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['description_html'] = mark_safe(markdown.markdown(self.object.description))
        return context

    def get_object(self):
        obj = super().get_object()
        obj.increment_views()
        return obj



class CategoryListView(ListView):
    model =  Category
    template_name = 'category/categories.html'
    ordering = 'title'
    page_kwarg = 'page'
    paginate_orphans = 3
    paginate_by = 9
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category/category.html'  
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
      
