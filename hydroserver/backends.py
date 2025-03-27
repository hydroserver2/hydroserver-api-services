from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


user_model = get_user_model()


class UnverifiedUserBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        unverified_users = user_model.objects.filter(
            unverified_email=email, is_verified=False
        )

        for user in unverified_users:
            if user and user.check_password(password):
                return user

        return None

    def get_user(self, user_id):
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
