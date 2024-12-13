import uuid
import base64
import urllib.parse
from datetime import timedelta
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from accounts.models.organization import Organization
from accounts.models.apikey import PermissionChecker
from django.conf import settings


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


account_verification_token = TokenGenerator()


class PersonManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):

        if email is not None:
            unverified_email = self.normalize_email(email)
        else:
            unverified_email = None

        if extra_fields.get('is_superuser') is True:
            user = self.model(
                username=email,
                email=email,
                is_verified=True,
                **extra_fields
            )
        else:
            uid = f'{uuid.uuid4()}@hydroserver-temp.org'

            if unverified_email is not None:
                self.model.objects.filter(unverified_email=unverified_email, is_verified=False).delete()

            user = self.model(
                username=uid,
                email=uid,
                unverified_email=unverified_email,
                **extra_fields
            )

        if password is not None:
            user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Person(AbstractUser):
    email = models.EmailField(unique=True)
    unverified_email = models.EmailField(blank=True, null=True)
    orcid = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    link = models.URLField(max_length=2000, blank=True, null=True)
    organization = models.OneToOneField(Organization, related_name='person', on_delete=models.SET_NULL,
                                        db_column='organizationId', blank=True, null=True)
    hydroshare_token = models.JSONField(blank=True, null=True)

    objects = PersonManager()

    @property
    def user_email(self) -> str:
        return self.email if self.is_verified is True else self.unverified_email

    @property
    def hydroshare_connected(self) -> bool:
        return True if self.hydroshare_token is not None else False

    @property
    def permissions(self):
        return getattr(self, '_permissions', PermissionChecker())

    @permissions.setter
    def permissions(self, permissions: PermissionChecker):
        self._permissions = permissions

    def update_account_to_verified(self):
        """
        Update the user's account to verified status.

        This function takes a user object as an argument and updates the `username`, `email`, `unverified_email`,
        and `is_verified` fields of that user. It then saves the updated user to the database and returns it.

        Parameters
        ----------
        self : user_model
            The user object that is being verified.

        Returns
        -------
        user_model
            The updated user object.
        """

        self.username = self.unverified_email
        self.email = self.unverified_email
        self.unverified_email = None
        self.is_verified = True
        self.save()

        return self

    def send_verification_email(self):
        """
        Send a verification email to the user.

        The function sends an email to the user with a link that they can click on to verify their account. It creates a
        context dictionary containing information about the user and token needed for verification. The function then
        renders an HTML template using this context dictionary, and uses Django's send_mail() method to send it as an
        email.

        Parameters
        ----------
        self : user_model
            The user object of the person who needs to verify their account.

        Returns
        -------
        None
        """

        context = {
            'uid': urllib.parse.quote(base64.b64encode(bytes(self.user_email, 'utf-8')).decode('utf-8')),
            'token': urllib.parse.quote(account_verification_token.make_token(self)),
            'name': self.first_name,
            'app_client_url': settings.APP_CLIENT_URL
        }

        html_message = render_to_string('verify_account_email.html', context)

        send_mail(
            'Verify HydroServer Account',
            '',  # Don't support plain text emails
            f'HydroServer <{settings.DEFAULT_FROM_EMAIL}>',
            [self.unverified_email],
            html_message=html_message,
        )

    def send_password_reset_confirmation_email(self, uid, token):
        """
        Send a password reset confirmation email to the user.

        This method sends an email to the user with a link to reset their password. The email includes the user ID and
        token required for resetting the password. The email is rendered using an HTML template.

        Parameters
        ----------
        uid : str
            The user ID required for password reset.
        token : str
            The token required for password reset.

        Returns
        -------
        None
        """

        mail_subject = 'Password Reset'

        context = {
            'user': self,
            'uid': uid,
            'token': token,
            'domain': 'hydroserver.ciroh.org',
            'app_client_url': settings.APP_CLIENT_URL
        }

        html_message = render_to_string('reset_password_email.html', context)

        send_mail(
            mail_subject,
            '',  # Don't support plain text emails
            f'HydroServer <{settings.DEFAULT_FROM_EMAIL}>',
            [self.email],
            html_message=html_message,
        )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


class PasswordReset(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    user = models.OneToOneField('Person', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.timestamp <= timedelta(days=1)


@receiver(pre_save, sender=Person)
def update_username_from_email(sender, instance, **kwargs):
    instance.username = instance.email
