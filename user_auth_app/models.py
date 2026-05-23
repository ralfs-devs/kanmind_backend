from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserProfileManager(BaseUserManager):
    """Custom manager for the UserProfile model.

    This manager overrides the default behavior to use email as the unique
    identifier for authentication instead of usernames.
    """

    def create_user(self, email, fullname, password=None, **extra_fields):
        """Creates and saves a standard user with the given email and fullname.

        Args:
            email (str): The unique email address for the user.
            fullname (str): The full name of the user.
            password (str, optional): The raw password for the user. Defaults to None.
            **extra_fields: Additional fields to be passed to the model constructor.

        Returns:
            UserProfile: The newly created user instance.
        """
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """Creates and saves a superuser with the given email and fullname.

        Ensures that administrative permissions (`is_staff` and `is_superuser`)
        are implicitly set to True.

        Args:
            email (str): The unique email address for the superuser.
            fullname (str): The full name of the superuser.
            password (str, optional): The raw password for the superuser. Defaults to None.
            **extra_fields: Additional fields to be passed to the model constructor.

        Returns:
            UserProfile: The newly created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, fullname, password, **extra_fields)


class UserProfile(AbstractUser):
    """Custom user model that represents a user profile within the system.

    This model extends Django's AbstractUser but drops the standard 'username'
    field in favor of using 'email' as the primary, unique identifier.

    Attributes:
        username (None): Explicitly disabled username field.
        fullname (models.CharField): The unique full name of the user.
        email (models.EmailField): The unique email address used for login.
        groups (models.ManyToManyField): Groups this user belongs to.
        user_permissions (models.ManyToManyField): Specific permissions for this user.
        USERNAME_FIELD (str): Field name used as the unique identifier ('email').
        REQUIRED_FIELDS (list): List of field names prompted for during createsuperuser.
        objects (UserProfileManager): The custom manager handling user creation.
    """
    username = None
    fullname = models.CharField(max_length=300, blank=False, unique=True)
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
        """Metadata options for the UserProfile model."""
        app_label = 'user_auth_app'
