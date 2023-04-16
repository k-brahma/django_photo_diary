from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom User model
    """

    def __str__(self):
        return self.email
