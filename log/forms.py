from django import forms

from log.models import Article, Comment


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'body', 'photo', 'tags']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', ]