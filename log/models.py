from django.conf import settings
from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='タグ名', )
    slug = models.SlugField(max_length=255, unique=True, )

    def __str__(self):
        return self.name


class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, )

    title = models.CharField(max_length=255, verbose_name='タイトル', )
    body = models.TextField(verbose_name='本文', )
    photo = models.ImageField(upload_to='log/photos/', blank=True, null=True, verbose_name='写真', )
    thumbnail = ImageSpecField(source='photo', processors=[ResizeToFill(100, 100)], format='JPEG',
                               options={'quality': 60}, )

    tags = models.ManyToManyField(Tag, blank=True, verbose_name='タグ', )

    created_at = models.DateTimeField(default=timezone.now, verbose_name='作成日時', )
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='更新日時', )

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(verbose_name='本文', )

    created_at = models.DateTimeField(default=timezone.now, verbose_name='作成日時', )
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='更新日時', )

    def __str__(self):
        return f'Comment to {self.article.title} by {self.body[:20]}'
