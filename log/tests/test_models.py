import shutil
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from log.models import Tag, Article

User = get_user_model()


class TestTag(TestCase):
    def test_str(self):
        tag = Tag.objects.create(name='タグ1', slug='tag1')
        self.assertEqual(str(tag), 'タグ1')


class TestArticle(TestCase):
    @classmethod
    def setUpTestData(cls):
        Article.photo.field.storage.location = 'media_test_dir'
        cls.user = User.objects.create(username='testuser', email='foo@bar.com', )

    def test_str(self):
        article = Article.objects.create(title='タイトル1', body='本文1', user=self.user)
        self.assertEqual(str(article), 'タイトル1')

    def test_photo(self):
        """
        写真投稿を含む場合
        photo, thubmnailが取得可能になっていることを確認する
        """
        path = Path(__file__).resolve().parent / 'test_img.png'
        with open(path, 'rb') as f:
            photo = SimpleUploadedFile('test_img.png', f.read(), content_type='image/png')
        article = Article.objects.create(title='タイトル1', body='本文1', photo=photo, user=self.user)
        self.assertTrue(article.photo)
        self.assertTrue(article.photo.url)
        self.assertTrue(article.thumbnail)
        self.assertTrue(article.thumbnail.url)

    @classmethod
    def tearDownClass(cls):
        """
        media_test_dir 以下のファイルをディレクトリごと削除
        """
        shutil.rmtree('media_test_dir')
        super().tearDownClass()


class TestComment(TestCase):
    def test_str(self):
        user = User.objects.create(username='testuser', email='foo@bar.com', )
        article = Article.objects.create(user=user, title='タイトル1', body='本文1')
        comment = article.comments.create(user=user, article=article, body='123456789012345678901234567890')
        self.assertEqual(str(comment), 'Comment to タイトル1 : 12345678901234567890')
