from django.test import TestCase


class TestSignUpPage(TestCase):
    """"
    signup page が無効になっていることを確認する
    """

    def test_signup_page_is_disabled(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'account/signup_closed.html')

        self.assertContains(response, '<title>ユーザー登録停止中</title>')
        self.assertContains(response, '<p>申し訳ありません、現在ユーザー登録を停止しています。</p>')

        self.assertNotContains(response, '<button type="submit">ユーザー登録 &raquo;</button>')
