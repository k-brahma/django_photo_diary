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
        cls.list_path = resolve_url('log:article_list')

        # テストユーザを作る。この作業は全テストを通じて一度で良いので setUpTestData で行う
        cls.user = User.objects.create_user(username='test', email='foo@bar.com',
                                            password='testpassword')

        # テスト用のタグを作成
        for i in range(1, 5):
            tag = Tag.objects.create(name=f'test_tag{i}', slug=f'test_tag{i}')
            setattr(cls, f'tag{i}', tag)

    def setUp(self):
        # テストの都度改めて article を作成する
        # 投稿編集テストがあるので、 setUpTestData で行うのは不適切
        # (更新された article のままだと他のテストに影響するため)
        self.article = Article.objects.create(title='base_test_title',
                                              body='base_test_body', user=self.user)
        self.article.tags.add(self.tag1, self.tag2)

        # aritcle の pk は生成される都度異なる場合があるので注意(データベース製品による)
        self.path = resolve_url('log:article_update', pk=self.article.pk)

    def result_redirect(self, response):
        """ 権限を持たないユーザが GET/POST でアクセスしたときのリダイレクト処理 """
        redirect_path = self.list_path
        self.assertRedirects(response, redirect_path, 302, 200,
                             fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者と管理者だけです。')

    def result_get_success(self, response):
        """ 権限を持つユーザが GET でアクセスしたときの処理 """
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_update.html')
        self.assertContains(response, self.article.title)

    def result_post_success(self, response):
        """ 権限を持つユーザが POST で日記の更新を行ったときの処理 """
        self.assertRedirects(response, self.list_path, 302, 200,
                             fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新しました。')

    def check_article(self, title, body, tags):
        """ post 後の article オブジェクトの状態チェック """
        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, title)
        self.assertEqual(articles[0].body, body)

        article_tags = articles[0].tags.all()
        self.assertEqual(len(article_tags), 2)
        self.assertIn(tags[0], article_tags)
        self.assertIn(tags[1], article_tags)

    def test_get_anonymous(self):
        """ AnonymousUser は一覧ページにリダイレクトされる """
        response = self.client.get(self.path, follow=True)
        self.result_redirect(response)

    def test_get_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path, follow=True)
        self.result_redirect(response)

    def test_get_article_user(self):
        """ 投稿者本人の場合は更新ページが表示される """
        result = self.client.login(email=self.user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.result_get_success(response)

    def test_get_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は更新ページが表示される """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com',
                                                password='testpassword', is_staff=True)
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.result_get_success(response)

    def test_post_failure_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は投稿に失敗し一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        # postメソッドで送信するデータを生成
        data = {
            'title': 'test_title_fail',
            'body': 'test_body_fail',
            'tags': [self.tag3.id, self.tag4.id, ]
        }
        response = self.client.post(self.path, data=data, follow=True)
        self.result_redirect(response)

        # データが更新されていないことを確認
        self.check_article('base_test_title', 'base_test_body', [self.tag1, self.tag2])

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

        self.result_post_success(response)

        # データが更新されていることを確認
        self.check_article('test_title1', 'test_body1', [self.tag3, self.tag4])

    def test_post_success_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は投稿を更新できる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com',
                                                password='testpassword', is_staff=True)
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        # postメソッドで送信するデータを生成
        data = {
            'title': 'test_title2',
            'body': 'test_body2',
            'tags': [self.tag3.id, self.tag4.id, ]
        }
        response = self.client.post(self.path, data=data, follow=True)

        self.result_post_success(response)

        # データが更新されていることを確認
        self.check_article('test_title2', 'test_body2', [self.tag3, self.tag4])


class TestArticleDeleteViewSample(TestCase):
    """
    ArticleDeleteView のテスト

    ページの表示/投稿の削除ができるのが投稿者本人または is_staff ユーザのみということを確認する
    """

    @classmethod
    def setUpTestData(cls):
        cls.list_path = resolve_url('log:article_list')
        cls.user = User.objects.create_user(username='test', email='foo@bar.com', password='testpassword')

    def setUp(self):
        self.article = Article.objects.create(title='base_test_title', body='base_test_body', user=self.user)
        self.path = resolve_url('log:article_delete', pk=self.article.pk)

    def result_redirect(self, response):
        """ 権限を持たないユーザが GET/POST でアクセスしたときのリダイレクト処理 """
        redirect_path = self.list_path
        self.assertRedirects(response, redirect_path, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除できるのは投稿者と管理者だけです。')

    def result_get_success(self, response):
        """ 権限を持つユーザが GET でアクセスしたときの処理 """
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log/article_delete.html')
        self.assertContains(response, self.article.title)

    def result_post_success(self, response):
        """ 権限を持つユーザが POST で日記の削除を行ったときの処理 """
        self.assertRedirects(response, self.list_path, 302, 200, fetch_redirect_response=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を削除しました。')

    def test_get_anonymous(self):
        """ AnonymousUser は一覧ページにリダイレクトされる """
        response = self.client.get(self.path, follow=True)
        self.result_redirect(response)

    def test_get_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path, follow=True)
        self.result_redirect(response)

    def test_get_article_user(self):
        """ 投稿者本人の場合は削除ページが表示される """
        result = self.client.login(email=self.user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.result_get_success(response)

    def test_get_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は削除ページが表示される """
        another_user = User.objects.create_user(is_staff=True, username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.get(self.path)
        self.result_get_success(response)

    def test_post_failure_another_user(self):
        """ 投稿者本人でなくてスタッフでもない場合は投稿に失敗し一覧ページにリダイレクトされる """
        another_user = User.objects.create_user(username='another', email='foo2@bar.com', password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        data = {'title': 'test_title_fail', 'body': 'test_body_fail'}  # postメソッドで送信するデータを生成
        response = self.client.post(self.path, data=data, follow=True)
        self.result_redirect(response)

        # オブジェクトが削除されていないことを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)

    def test_post_success_article_user(self):
        """ 投稿者本人の場合は投稿を削除できる """
        self.client.force_login(self.user)  # ログイン状態にする

        response = self.client.post(self.path, data={}, follow=True)

        self.result_post_success(response)

        # オブジェクトが削除されていることを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 0)

    def test_post_success_is_staff(self):
        """ 投稿者本人でなくてもスタッフの場合は投稿を削除できる """
        another_user = User.objects.create_user(is_staff=True, username='another', email='foo2@bar.com',
                                                password='testpassword')
        result = self.client.login(email=another_user.email, password='testpassword')
        self.assertTrue(result)  # ログイン成功しているか確認

        response = self.client.post(self.path, data={}, follow=True)

        self.result_post_success(response)

        # オブジェクトが削除されていることを確認
        articles = Article.objects.all()
        self.assertEqual(len(articles), 0)
