import shutil
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from log.models import Article, Tag, Comment

User = get_user_model()


class ArticleListView(TestCase):
    """
    ArticleListView のテスト

    表示すべきアイテムがあり/なしのときに生成される HTML を調べる
    """

    @classmethod
    def setUpTestData(cls):
        cls.path = reverse('log:article_list')

    def test_none(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_list.html')
        self.assertContains(response, '記事一覧')

        self.assertNotContains(response, 'test_title')
        self.assertContains(response, 'まだ日記がありません。')

    def test_exists(self):
        user = User.objects.create_user(username='test', email='foo@bar.com', password='test')
        Article.objects.create(title='test_title', body='test_body', user=user, )
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_list.html')
        self.assertContains(response, '記事一覧')

        self.assertContains(response, 'test_title')
        self.assertNotContains(response, 'まだ日記がありません。')


class TestArticleTagListView(TestCase):
    """
    ArticleTagListView のテスト

    タグに合致したものだけが表示されることを確認する
    """

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name='test_name', slug='test_slug')
        cls.path = reverse('log:article_tag_list', kwargs={'slug': cls.tag.slug})
        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='test')

    def test_none(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_list.html')
        self.assertContains(response, '記事一覧')

        self.assertNotContains(response, 'test_title')
        self.assertContains(response, 'まだ日記がありません。')

    def test_exists_not_tag(self):
        """
        タグが一致しないのでヒットしない
        """
        Article.objects.create(title='test_title', body='test_body', user=self.user, )
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_list.html')
        self.assertContains(response, '記事一覧')

        self.assertNotContains(response, 'test_title')
        self.assertContains(response, 'まだ日記がありません。')

    def test_exists_tag(self):
        """
        タグが一致するのでヒットする
        """
        article = Article.objects.create(title='test_title', body='test_body', user=self.user, )
        article.tags.add(self.tag)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_list.html')
        self.assertContains(response, '記事一覧')

        self.assertContains(response, 'test_title')
        self.assertNotContains(response, 'まだ日記がありません。')


class TestArticleDetailView(TestCase):
    """
    ArticleDetailView のテスト

    200, 404 if not found.
    """

    @classmethod
    def setUpTestData(cls):
        cls.pk = 1
        cls.path = reverse('log:article_detail', kwargs={'pk': cls.pk})
        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='test')

    def test_not_exists(self):
        """
        not found 404
        """
        self.assertFalse(Article.objects.filter(pk=self.pk).exists())

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 404)

    def test_exists(self):
        article = Article.objects.create(pk=1, title='test_title', body='test_body', user=self.user, )

        self.assertTrue(Article.objects.filter(pk=self.pk).exists())

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        article = Article.objects.create(pk=1, title='test_title', body='test_body', user=self.user, )

        self.assertTrue(Article.objects.filter(pk=self.pk).exists())

        self.client.force_login(self.user)
        response = self.client.post(self.path, data={'body': 'test_comment'}, follow=True)
        self.assertRedirects(response, self.path, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'コメントを投稿しました。')

        comments = Comment.objects.all()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].body, 'test_comment')
        self.assertEqual(comments[0].article, article)

    def test_post_failure_body_empty(self):
        article = Article.objects.create(pk=1, title='test_title', body='test_body', user=self.user, )

        self.assertTrue(Article.objects.filter(pk=self.pk).exists())

        self.client.force_login(self.user)
        response = self.client.post(self.path, data={'body': ''}, follow=True)
        self.assertRedirects(response, self.path, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'コメントを入力してください。')

        comments = Comment.objects.all()
        self.assertEqual(len(comments), 0)

    def test_post_failure_not_login(self):
        article = Article.objects.create(pk=1, title='test_title', body='test_body', user=self.user, )

        self.assertTrue(Article.objects.filter(pk=self.pk).exists())

        response = self.client.post(self.path, data={'body': 'test_comment'}, follow=True)
        self.assertRedirects(response, resolve_url('account_login'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'コメントするにはログインしてください。')

        comments = Comment.objects.all()
        self.assertEqual(len(comments), 0)


class TestArticleCreateView(TestCase):
    """
    ArticleCreateView のテスト

    ログイン状態によってリダイレクトされることがある
    投稿については、正常系、異常系についてテスト
    """

    @classmethod
    def setUpTestData(cls):
        # テストでアップロードされた画像が保存されるディレクトリを変更
        Article.photo.field.storage.location = 'media_root_test'

        cls.path = reverse('log:article_create')
        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='test')

        cls.tag1 = Tag.objects.create(name='test_tag1', slug='test_tag1')
        cls.tag2 = Tag.objects.create(name='test_tag2', slug='test_tag2')

    def test_not_login(self):
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を投稿するにはログインしてください。')

    def test_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_create.html')

    def test_post_success_title_body_only(self):
        self.client.force_login(self.user)
        response = self.client.post(self.path, data={'title': 'test_title', 'body': 'test_body'}, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を投稿しました。')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'test_title')
        self.assertEqual(articles[0].body, 'test_body')

    def test_post_success_title_body_photo_tag(self):
        self.client.force_login(self.user)

        path = Path(__file__).resolve().parent / 'test_img.png'
        with open(path, 'rb') as f:
            photo = SimpleUploadedFile('test_img.png', f.read(), content_type='image/png')

        response = self.client.post(self.path, data={'title': 'test_title', 'body': 'test_body', 'photo': photo,
                                                     'tags': [self.tag1.id, self.tag2.id, ]}, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を投稿しました。')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'test_title')
        self.assertEqual(articles[0].body, 'test_body')
        self.assertEqual(articles[0].photo.size, photo.size)
        tags = list(articles[0].tags.all())
        self.assertEqual(len(tags), 2)
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)

    def test_post_failure_photo_not_image(self):
        self.client.force_login(self.user)
        response = self.client.post(self.path, data={'title': 'test_title', 'body': 'test_body',
                                                     'photo': SimpleUploadedFile('test_img.txt', b'not image')},
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を投稿できませんでした。')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 0)

    @classmethod
    def tearDownClass(cls):
        """
        media_root_test 以下のファイルをディレクトリごと削除
        """
        shutil.rmtree('media_root_test')
        super().tearDownClass()


class TestArticleUpdateView(TestCase):
    """
    ArticleUpdateView のテスト

    ログイン状態によってリダイレクトされることがある
    投稿については、正常系、異常系についてテスト
    """

    @classmethod
    def setUpTestData(cls):
        # テストでアップロードされた画像が保存されるディレクトリを変更
        Article.photo.field.storage.location = 'media_root_test'

        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='test')

        cls.tag1 = Tag.objects.create(name='test_tag1', slug='test_tag1')
        cls.tag2 = Tag.objects.create(name='test_tag2', slug='test_tag2')

    def setUp(self):
        super().setUp()
        path = Path(__file__).resolve().parent / 'test_img.png'
        with open(path, 'rb') as f:
            photo = SimpleUploadedFile('test_img.png', f.read(), content_type='image/png')
        self.article = Article.objects.create(title='base_test_title', body='base_test_body', photo=photo,
                                              user=self.user)
        self.article.tags.add(self.tag1)
        self.path = resolve_url('log:article_update', pk=self.article.pk)

    def test_not_login(self):
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者だけです。')

    def test_another_user(self):
        another_user = User.objects.create_user(username='another', email='foo2@bar.com')
        self.client.force_login(another_user)
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者だけです。')

    def test_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_update.html')

    def test_post_success_title_body_only(self):
        self.client.force_login(self.user)
        response = self.client.post(self.path, data={'title': 'test_title', 'body': 'test_body'}, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新しました。')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'test_title')
        self.assertEqual(articles[0].body, 'test_body')

    def test_post_success_title_body_photo_tag(self):
        self.client.force_login(self.user)

        path = Path(__file__).resolve().parent / 'test_img.png'
        with open(path, 'rb') as f:
            photo = SimpleUploadedFile('test_img.png', f.read(), content_type='image/png')
        response = self.client.post(self.path, data={'title': 'test_title', 'body': 'test_body', 'photo': photo,
                                                     'tags': [self.tag1.id, self.tag2.id, ]}, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新しました。')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'test_title')
        self.assertEqual(articles[0].body, 'test_body')
        self.assertEqual(articles[0].photo.size, photo.size)
        tags = list(articles[0].tags.all())
        self.assertEqual(len(tags), 2)
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)

    def test_post_failure_photo_not_image(self):
        self.client.force_login(self.user)
        response = self.client.post(self.path, data={'title': 'test_title', 'body': 'test_body',
                                                     'photo': SimpleUploadedFile('test_img.txt', b'not image')},
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を編集できませんでした。')

    @classmethod
    def tearDownClass(cls):
        """
        media_root_test 以下のファイルをディレクトリごと削除
        """
        shutil.rmtree('media_root_test')
        super().tearDownClass()


class TestArticleDeleteView(TestCase):
    """
    ArticleDeleteView のテスト

    ログイン状態によってリダイレクトされることがある
    投稿については、正常系、異常系についてテスト
    """

    def setUp(self):
        # テストでアップロードされた画像が保存されるディレクトリを変更
        self.user = User.objects.create_user(username='test', email='foo@bar.com', password='test')

        self.article = Article.objects.create(title='base_test_title', body='base_test_body', user=self.user)
        self.path = resolve_url('log:article_delete', pk=self.article.pk)

    def test_not_login(self):
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除できるのは投稿者だけです。')

    def test_another_user(self):
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='test')
        self.client.force_login(another_user)
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除できるのは投稿者だけです。')

    def test_login(self):
        self.client.force_login(self.user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_delete.html')

    def test_post_success(self):
        self.client.force_login(self.user)
        response = self.client.post(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除しました。')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 0)


class TestTagCreateView(TestCase):
    """
    TagCreateView のテスト

    user.is_staff かどうかでリダイレクトされることがある
    """

    @classmethod
    def setUpTestData(cls):
        cls.path = resolve_url('log:tag_create')

    def test_anonymous(self):
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを作成できるのは管理者だけです。')

    def test_not_staff(self):
        user = User.objects.create_user(is_staff=False, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを作成できるのは管理者だけです。')

    def test_staff(self):
        user = User.objects.create_user(is_staff=True, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/tag_create.html')

    def test_post_success(self):
        user = User.objects.create_user(is_staff=True, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.post(self.path, data={'name': 'test_tag', 'slug': 'test_slug', }, follow=True)
        self.assertRedirects(response, resolve_url('log:tag_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを作成しました。')


class TestTagUpdateView(TestCase):
    """
    TagUpdateView のテスト

    user.is_staff かどうかでリダイレクトされることがある
    """

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name='base_test_tag', slug='base_test_slug')
        cls.path = resolve_url('log:tag_update', pk=cls.tag.pk)

    def test_anonymous(self):
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを更新できるのは管理者だけです。')

    def test_not_staff(self):
        user = User.objects.create_user(is_staff=False, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを更新できるのは管理者だけです。')

    def test_staff(self):
        user = User.objects.create_user(is_staff=True, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/tag_update.html')

    def test_post_success(self):
        user = User.objects.create_user(is_staff=True, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.post(self.path, data={'name': 'test_tag', 'slug': 'test_slug', }, follow=True)
        self.assertRedirects(response, resolve_url('log:tag_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを更新しました。')


class TestTagDeleteView(TestCase):
    """
    TagDeleteView のテスト

    user.is_staff かどうかでリダイレクトされることがある
    """

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name='base_test_tag', slug='base_test_slug')
        cls.path = resolve_url('log:tag_delete', pk=cls.tag.pk)

    def test_anonymous(self):
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを削除できるのは管理者だけです。')

    def test_not_staff(self):
        user = User.objects.create_user(is_staff=False, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを削除できるのは管理者だけです。')

    def test_staff(self):
        user = User.objects.create_user(is_staff=True, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/tag_delete.html')

    def test_post_success(self):
        user = User.objects.create_user(is_staff=True, username='test', email='foo@bar.com')
        self.client.force_login(user)
        response = self.client.post(self.path, data={}, follow=True)
        self.assertRedirects(response, resolve_url('log:tag_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'タグを削除しました。')

        self.assertEqual(Tag.objects.count(), 0)
