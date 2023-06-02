""" views.py のテストコードのサンプル。
初心者向けのシンプルな解説とするため、画像の投稿にかかる処理は省略している。
"""
from django.shortcuts import resolve_url
from django.test import TestCase
from django.contrib.auth import get_user_model

from log.models import Article, Tag

User = get_user_model()


class TestArticleUpdateViewSample(TestCase):
    """
    ArticleUpdateView のテスト

    ページの表示/投稿の更新ができるのが投稿者本人または is_staff ユーザのみということを確認する
    """

    @classmethod
    def setUpTestData(cls):
        # テストユーザを作る。この作業は全テストを通じて一度で良いので setUpTestData で行う
        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='testpassword')

        # テスト用のタグを作成
        for i in range(1, 5):
            tag = Tag.objects.create(name=f'test_tag{i}', slug=f'test_tag{i}')
            setattr(cls, f'tag{i}', tag)

    def setUp(self):
        # テストの都度改めて article を作成する
        # 投稿編集テストがあるので、 setUpTestData で行うのは不適切
        # (更新された article のままだと他のテストに影響するため)
        self.article = Article.objects.create(title='base_test_title', body='base_test_body',
                                              user=self.user)
        self.article.tags.add(self.tag1, self.tag2)

        # aritcle の pk は生成される都度異なる場合があるので注意(データベース製品による)
        self.path = resolve_url('log:article_update', pk=self.article.pk)

    def test_get_anonymous(self):
        """ AnonymousUser は一覧ページにリダイレクトされる """
        response = self.client.get(self.path, follow=True)

        redirect_url = resolve_url('log:article_list')
        self.assertRedirects(response, redirect_url, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者と管理者だけです。')

    def test_get_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path, follow=True)

        redirect_url = resolve_url('log:article_list')
        self.assertRedirects(response, redirect_url, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者と管理者だけです。')

    def test_get_article_user(self):
        """ 投稿者本人の場合は更新ページが表示される """
        result = self.client.login(email=self.user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_update.html')

    def test_get_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は更新ページが表示される """
        another_user = User.objects.create_user(is_staff=True, username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_update.html')

    def test_post_failure_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は投稿に失敗し一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        # postメソッドで送信するデータを生成
        data = {
            'title': 'test_title_fail',
            'body': 'test_body_fail',
            'tags': [self.tag3.id, self.tag4.id, ]
        }
        response = self.client.post(self.path, data=data, follow=True)

        redirect_url = resolve_url('log:article_list')
        self.assertRedirects(response, redirect_url, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者と管理者だけです。')

        # データが更新されていないことを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'base_test_title')
        self.assertEqual(articles[0].body, 'base_test_body')

        tags = articles[0].tags.all()
        self.assertEqual(len(tags), 2)
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)

    def test_post_success_article_user(self):
        """ 投稿者本人の場合は投稿を更新できる """
        self.client.force_login(self.user)  # ログイン状態にする

        # postメソッドで送信するデータを生成
        data = {
            'title': 'test_title1',
            'body': 'test_body1',
            'tags': [self.tag3.id, self.tag4.id, ]
        }
        response = self.client.post(self.path, data=data, follow=True)

        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新しました。')

        # データが更新されていることを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'test_title1')
        self.assertEqual(articles[0].body, 'test_body1')

        tags = articles[0].tags.all()
        self.assertEqual(len(tags), 2)
        self.assertIn(self.tag3, tags)
        self.assertIn(self.tag4, tags)

    def test_post_success_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は投稿を更新できる """
        another_user = User.objects.create_user(is_staff=True, username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        # postメソッドで送信するデータを生成
        data = {
            'title': 'test_title2',
            'body': 'test_body2',
            'tags': [self.tag3.id, self.tag4.id, ]
        }
        response = self.client.post(self.path, data=data, follow=True)

        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新しました。')

        # データが更新されていることを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'test_title2')
        self.assertEqual(articles[0].body, 'test_body2')

        tags = articles[0].tags.all()
        self.assertEqual(len(tags), 2)
        self.assertIn(self.tag3, tags)
        self.assertIn(self.tag4, tags)


class TestArticleDeleteViewSample(TestCase):
    """
    ArticleDeleteView のテスト

    ページの表示/投稿の削除ができるのが投稿者本人または is_staff ユーザのみということを確認する
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='testpassword')

    def setUp(self):
        self.article = Article.objects.create(title='base_test_title', body='base_test_body', user=self.user)
        self.path = resolve_url('log:article_delete', pk=self.article.pk)

    def test_get_anonymous(self):
        """ AnonymousUser は一覧ページにリダイレクトされる """
        response = self.client.get(self.path, follow=True)

        redirect_url = resolve_url('log:article_list')
        self.assertRedirects(response, redirect_url, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除できるのは投稿者と管理者だけです。')

    def test_get_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path, follow=True)

        redirect_url = resolve_url('log:article_list')
        self.assertRedirects(response, redirect_url, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除できるのは投稿者と管理者だけです。')

    def test_get_article_user(self):
        """ 投稿者本人の場合は更新ページが表示される """
        result = self.client.login(email=self.user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_delete.html')

    def test_get_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は更新ページが表示される """
        another_user = User.objects.create_user(is_staff=True, username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_delete.html')

    def test_post_failure_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は投稿に失敗し一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        data = {'title': 'test_title_fail', 'body': 'test_body_fail'}  # postメソッドで送信するデータを生成
        response = self.client.post(self.path, data=data, follow=True)

        redirect_url = resolve_url('log:article_list')
        self.assertRedirects(response, redirect_url, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除できるのは投稿者と管理者だけです。')

        # データが削除されていないことを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)

    def test_post_success_article_user(self):
        """ 投稿者本人の場合は投稿を更新できる """
        self.client.force_login(self.user)  # ログイン状態にする

        response = self.client.post(self.path, data={}, follow=True)

        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除しました。')

        # データが削除されていることを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 0)

    def test_post_success_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は投稿を更新できる """
        another_user = User.objects.create_user(is_staff=True, username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.post(self.path, data={}, follow=True)

        self.assertRedirects(response, resolve_url('log:article_list'), 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除しました。')

        # データが削除されていることを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 0)
