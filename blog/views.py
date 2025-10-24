from django.views.generic import ListView, DetailView , CreateView
from django.utils.safestring import mark_safe
from .models import Blog, Category , Comment
import markdown
from django.db.models import Q
from accounts.mixins import AuthenticatedAccessMixin
from .forms import CommentForm
from .utils import filter_and_sort_blogs
from .mixins import SearchAndSortContextMixin



class BlogListView(SearchAndSortContextMixin , ListView):
    model = Blog
    template_name = 'blog/blog_list.html'
    ordering = ['-created_at']
    page_kwarg = 'page'
    paginate_orphans = 3
    paginate_by = 9
    context_object_name = 'blogs'

    def get_queryset(self):
        queryset = Blog.active_objects.all()
        return filter_and_sort_blogs(queryset, self.request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.active_objects.all()
        return context


        


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        description = getattr(self.object, 'description', '')
        context['description_html'] = mark_safe(markdown.markdown(description))
        context['form'] = CommentForm()
        context['related_blogs'] = Blog.active_objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if hasattr(obj, 'increment_views'):
            obj.increment_views()
        return obj


class CategoryListView(ListView):
    model = Category
    template_name = 'category/categories.html'
    ordering = ['title']
    page_kwarg = 'page'
    paginate_orphans = 3
    paginate_by = 9
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.active_objects.all()


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category/category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blogs = Blog.active_objects.filter(category=self.object)
        context['blogs'] = blogs
        return context


class CommentCreateView(AuthenticatedAccessMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.blog = Blog.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.blog.get_absolute_url()
