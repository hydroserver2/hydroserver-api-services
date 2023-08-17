from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model


user_model = get_user_model()


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


account_activation_token = TokenGenerator()


def update_account_to_verified(user: user_model):
    """"""

    user.username = user.unverified_email
    user.email = user.unverified_email
    user.unverified_email = None
    user.is_verified = True
    user.save()

    return user
