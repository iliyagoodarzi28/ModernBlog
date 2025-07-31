# mixins.py
from .utils import filter_and_sort_blogs

class SearchAndSortContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['sort'] = self.request.GET.get('sort', 'new')
        return context

class BlogFilterSortMixin(SearchAndSortContextMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_and_sort_blogs(queryset, self.request)
