from django.test import TestCase


class TestHome(TestCase):
    """
    Home page exists at /.
    """

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_html(self):
        response = self.client.get('/')
        self.assertContains(response, '<li class="breadcrumb-item active" aria-current="page">ホーム</li>')
    