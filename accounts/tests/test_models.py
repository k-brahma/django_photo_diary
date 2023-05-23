from django.test import TestCase

from django.contrib.auth import get_user_model

User = get_user_model()


class TestCustomUser(TestCase):
    """
    CustomUser.__str__() returns self.email.
    """

    def test_str(self):
        user = User.objects.create_user(username='testuser', email='foo@bar.com', )
        self.assertEqual(str(user), 'foo@bar.com')
