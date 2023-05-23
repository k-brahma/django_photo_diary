from django.test import TestCase

from accounts.adapter import NoNewUsersAccountAdapter


class TestNoNewUsersAccountAdapter(TestCase):
    """
    NoNewUsersAccountAdapter.is_open_for_signup() always returns False.
    """

    def test_is_open_for_signup(self):
        adapter = NoNewUsersAccountAdapter()
        result = adapter.is_open_for_signup(None)

        self.assertFalse(result)
