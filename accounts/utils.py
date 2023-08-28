import base64
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.conf import settings


user_model = get_user_model()


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


account_verification_token = TokenGenerator()


def send_verification_email(user: user_model):
    """
    The send_verification_email function sends an email to the user with a link that they can click on to verify their
    account. The function takes in one parameter, which is the user object of the person who needs to verify their
    account. The function then creates a context dictionary containing information about the user and token needed for
    verification. It then renders an HTML template using this context dictionary, and uses Django's send_mail() method
    to send it as an email.

    :param user: user_model: Pass the user object to the function
    :return: None
    """

    context = {
        'uid': base64.b64encode(bytes(user.email, 'utf-8')).decode('utf-8'),
        'token': account_verification_token.make_token(user),
        'name': user.first_name,
        'proxy_base_url': settings.PROXY_BASE_URL
    }

    html_message = render_to_string('verify_account_email.html', context)

    send_mail(
        'Verify HydroServer Account',
        '',  # Don't support plain text emails
        f'HydroServer <{settings.DEFAULT_FROM_EMAIL}>',
        [user.unverified_email],
        html_message=html_message,
    )


def update_account_to_verified(user: user_model):
    """
    The update_account_to_verified function takes a user object as an argument and updates the username, email,
    unverified_email, is_verified fields of that user. It then saves the updated user to the database and returns it.

    :param user: user_model: Pass in the user object that is being verified
    :return: The user object
    """

    user.username = user.unverified_email
    user.email = user.unverified_email
    user.unverified_email = None
    user.is_verified = True
    user.save()

    return user


def send_password_reset_confirmation_email(user, uid, token):
    mail_subject = 'Password Reset'

    context = {
        'user': user,
        'uid': uid,
        'token': token,
        'domain': 'hydroserver.ciroh.org',
        'proxy_base_url': settings.PROXY_BASE_URL
    }

    html_message = render_to_string('reset_password_email.html', context)

    send_mail(
        mail_subject,
        '',  # Don't support plain text emails
        f'HydroServer <{settings.DEFAULT_FROM_EMAIL}>',
        [user.email],
        html_message=html_message,
    )
