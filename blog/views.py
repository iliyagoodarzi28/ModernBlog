from django.views.generic import ListView, DetailView , CreateView
from django.utils.safestring import mark_safe
from .models import Blog, Category , Comment
import markdown
from django.db.models import Q
from accounts.mixins import AuthenticatedAccessMixin
from .forms import CommentForm



class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog.html'
    ordering = ['-date']
    page_kwarg = 'page'
    paginate_orphans = 3
    paginate_by = 9
    context_object_name = 'blogs'

    def get_queryset(self):
        queryset = Blog.active_objects.all()

        # Search
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        # Sort
        sort_by = self.request.GET.get('sort')
        if sort_by == 'new':
            queryset = queryset.order_by('-date')
        elif sort_by == 'old':
            queryset = queryset.order_by('date')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views')
        else:
            queryset = queryset.order_by('-date')  # پیش‌فرض

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['sort'] = self.request.GET.get('sort', 'new')
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


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category/category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'



class CommentCreateView(AuthenticatedAccessMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.blog = Blog.objects.get(slug=self.kwargs['slug'])  # یا pk
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.blog.get_absolute_url()


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
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if hasattr(obj, 'increment_views'):
            obj.increment_views()
        return obj
