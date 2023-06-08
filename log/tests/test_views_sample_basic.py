from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import TestCase

from log.models import Article


class TestArticleListViewSample(TestCase):
    """ 未ログインユーザ、ログインユーザでの GET リクエストのテストの例 """

    def test_anonymous(self):
        """ 未ログインユーザとしてGETリクエストを実施 """
        path = resolve_url('log:article_list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)

    def test_authed_user(self):
        """ ログインユーザとしてGETリクエストを実施 """
        user = get_user_model().objects.create_user(
            username='testuser', email='foo@bar.com', password='testpassword')
        login_result = self.client.login(email=user.email, password='testpassword')
        self.assertTrue(login_result)

        path = resolve_url('log:article_list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)


class TestRedirectClient(TestCase):
    """
    client.get() でのリダイレクトのテストの例
    follow=True/False での挙動の違いを確認する
    """

    def setUp(self):
        """ 3つのテストメソッドに共通の準備 """
        user = get_user_model().objects.create_user(
            username='test', email='foo@bar.com', password='testpassword')
        article = Article.objects.create(
            title='base_test_title', body='base_test_body', user=user)

        self.redirect_path = resolve_url('log:article_list')
        self.path = resolve_url('log:article_update', pk=article.pk)

    def test_follow_false(self):
        """ follow=False のとき、リダイレクト先のページを取得しない """
        response = self.client.get(self.path, follow=False)

        # リダイレクトコードを受け取るところまでしか処理を進めないので、ステータスコードは 302
        self.assertEqual(response.status_code, 302)

        # リダイレクト先ページのHTMLを取得しない
        html = response.content.decode('utf-8')
        self.assertEqual(html, "")

        # リダイレクト先ページの context を取得しない
        self.assertIsNone(response.context)

    def test_follow_true(self):
        """ follow=True  のとき、リダイレクト先のページを取得する """
        response = self.client.get(self.path, follow=True)

        # リダイレクト先ページを取得するので、ステータスコードは 200
        self.assertEqual(response.status_code, 200)

        # リダイレクト先ページのHTMLを取得するので、空のコンテンツではない
        html = response.content.decode('utf-8')
        self.assertNotEqual(html, "")

        # リダイレクト先ページの context を取得するので、Noneではない
        self.assertIsNotNone(response.context)

    def test_default(self):
        """ follow のデフォルト値は False """
        response = self.client.get(self.path, follow=False)

        self.assertEqual(response.status_code, 302)

        html = response.content.decode('utf-8')
        self.assertEqual(html, "")

        self.assertIsNone(response.context)


class TestRedirectAssertRedirect(TestCase):
    """
    assertRedirects() の挙動をテスト
    fetch_redirect_response=True/False での挙動の違いを確認する
    """

    def setUp(self):
        """ 3つのテストメソッドに共通の準備 """
        user = get_user_model().objects.create_user(
            username='test', email='foo@bar.com', password='testpassword')
        article = Article.objects.create(
            title='base_test_title', body='base_test_body', user=user)

        self.redirect_path = resolve_url('log:article_list')
        self.path = resolve_url('log:article_update', pk=article.pk)

    def test_fetch_redirect_response_false(self):
        """ fetch_redirect=False のとき、assertRedirects メソッドは、
            リダイレクト先の検証を行わない """
        response = self.client.get(self.path)

        self.assertRedirects(
            response, self.redirect_path,
            target_status_code=500,  # リダイレクト先の検証を行わないのでこの値は無視される
            fetch_redirect_response=False)

    def test_fetch_redirect_response_true(self):
        """ fetch_redirect=True のとき、assertRedirects メソッドは、
            内部でリダイレクト先へのリクエストを発行し、ステータスコードの検証を行う """
        response = self.client.get(self.path)

        # target_status_code は 正しい値なのでOK
        self.assertRedirects(response, self.redirect_path, target_status_code=200,
                             fetch_redirect_response=True)

        # target_status_code は 正しい値ではないのでこれはNG
        # self.assertRedirects(response, self.redirect_path,
        #                      target_status_code=500,  # リダイレクト先の検証を行うのでこれはNG
        #                      fetch_redirect_response=True)

    def test_fetch_redirect_response_default(self):
        """ fetch_redirect のデフォルト値は True """
        response = self.client.get(self.path)

        # target_status_code は 正しい値なのでOK
        self.assertRedirects(response, self.redirect_path, target_status_code=200, )

        # target_status_codeの初期値は 200 なので以下でもOK
        self.assertRedirects(response, self.redirect_path)

        # 以下は、そのほかの初期値もあえて指定したもの
        self.assertRedirects(response, self.redirect_path,
                             status_code=302,
                             target_status_code=200)
        self.assertRedirects(response, self.redirect_path,
                             status_code=302,
                             target_status_code=200,
                             fetch_redirect_response=True)

        # target_status_code は 正しい値ではないのでこれはNG
        # self.assertRedirects(response, self.redirect_path, target_status_code=500, )


class TestRedirectVariousCases(TestCase):
    """ 種々のニーズに対応したリダイレクトのテスト方法まとめ """

    def setUp(self):
        """ 3つのテストメソッドに共通の準備 """
        user = get_user_model().objects.create_user(
            username='test', email='foo@bar.com', password='testpassword')
        article = Article.objects.create(
            title='base_test_title', body='base_test_body', user=user)

        self.redirect_path = resolve_url('log:article_list')
        self.path = resolve_url('log:article_update', pk=article.pk)

    def test_assert_status_code_only(self):
        """ リダイレクト元でのスタータスコードを検査したいだけのとき"""
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 302)

    def test_assert_redirect_status_code(self):
        """ リダイレクト先のステータスコードを検査したいだけのとき """
        response = self.client.get(self.path, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_assert_redirect_page_content(self):
        """ リダイレクト先のコンテンツを検査したいいとき """
        response = self.client.get(self.path, follow=True)

        html = response.content.decode('utf-8')
        self.assertNotEqual(html, "")

        self.assertContains(response, '記事一覧')

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '日記を更新できるのは投稿者と管理者だけです。')

    def test_assert_redirect(self):
        """ リダイレクト元とリダイレクト先のスタータスコードの両方を検査したいとき """
        response = self.client.get(self.path, follow=True)
        self.assertRedirects(response, self.redirect_path,
                             status_code=302, target_status_code=200)

        # status_code=302, target_status_code=200 はともに初期値なので省略可能
        self.assertRedirects(response, self.redirect_path)
