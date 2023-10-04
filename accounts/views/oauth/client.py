from authlib.integrations.django_client import OAuth
from django.contrib.auth import get_user_model

oauth = OAuth()
user_model = get_user_model()