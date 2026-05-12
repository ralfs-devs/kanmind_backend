from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserProfileManager(BaseUserManager):
    def create_user(self, email, fullname, password=None, **extra_fields):
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, fullname, password, **extra_fields)


class UserProfile(AbstractUser):
    username = None
    fullname = models.CharField(max_length=300, blank=False)
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='userprofile_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='userprofile_permissions_set'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    objects = UserProfileManager()

    class Meta:
        app_label = 'user_auth_app'
