from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from log.forms import ArticleForm, CommentForm
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

    def post(self, request, *args, **kwargs):
        """
        コメント投稿
        """
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'コメントするにはログインしてください。')
            return redirect('account_login')

        article = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.article = article
            form.instance.user = self.request.user
            form.save()
            messages.success(self.request, 'コメントを投稿しました。')
        else:
            messages.error(self.request, 'コメントを入力してください。')
        return redirect(self.request.path)


class ArticleCreateView(CreateView):
    model = Article
    template_name = 'log/article_create.html'
    form_class = ArticleForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '日記を投稿するにはログインしてください。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '日記を投稿しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '日記を投稿できませんでした。')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('log:article_list')


class ArticleUpdateView(UpdateView):
    template_name = 'log/article_update.html'
    model = Article
    form_class = ArticleForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user == self.object.user:
            messages.error(request, '日記を更新できるのは投稿者だけです。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '日記を編集できませんでした。')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('log:article_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = self.object
        return context


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'log/article_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user == self.object.user:
            messages.error(request, '日記を削除できるのは投稿者だけです。')
            return redirect('log:article_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, '日記を削除しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('log:article_list')


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
            messages.error(request, 'タグを作成できるのは管理者だけです。')
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
            messages.error(request, 'タグを更新できるのは管理者だけです。')
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
            messages.error(request, 'タグを削除できるのは管理者だけです。')
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
