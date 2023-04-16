from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from log.forms import ArticleForm
from log.models import Article, Tag


class ArticleListView(ListView):
    model = Article
    template_name = 'log/article_list.html'
    context_object_name = 'articles'
    paginate_by = 5

    def get_queryset(self):
        return Article.objects.select_related('user').prefetch_related('tags', 'comments', 'comments__user', ).order_by(
            '-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        page_obj = context['page_obj']
        context['paginator_range'] = page_obj.paginator.get_elided_page_range(page_obj.number)
        return context


class ArticleTagListView(ArticleListView):
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return super().get_queryset().filter(tags=self.tag)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'log/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.select_related('user').prefetch_related('tags', 'comments', 'comments__user', ).order_by(
            '-created_at')


class ArticleCreateView(CreateView):
    model = Article
    template_name = 'log/article_create.html'
    form_class = ArticleForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '権限がありません。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '記事を作成しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log:article_list')


class ArticleUpdateView(ArticleCreateView):
    template_name = 'log/article_update.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '権限がありません。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '記事を更新しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log:article_list')


class ArticleDeleteView(ArticleCreateView):
    template_name = 'log/article_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '権限がありません。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '記事を削除しました。')
        return super().form_valid(form)


class TagListView(ListView):
    model = Tag
    template_name = 'log/tag_list.html'
    context_object_name = 'tags'


class TagCreateView(CreateView):
    model = Tag
    template_name = 'log/tag_create.html'
    fields = ['name', 'slug']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '権限がありません。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'タグを作成しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log:tag_list')


class TagUpdateView(UpdateView):
    model = Tag
    template_name = 'log/tag_update.html'
    fields = ['name', 'slug']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '権限がありません。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'タグを更新しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log:tag_list')


class TagDeleteView(DeleteView):
    model = Tag
    template_name = 'log/tag_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '権限がありません。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'タグを削除しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_list_url'] = resolve_url('log:tag_list')
        return context
