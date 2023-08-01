from authlib.integrations.django_client import OAuth

oauth = OAuth()
oauth.register(
    name='orcid',
    client_kwargs={'scope': 'openid email profile'},
    response_type= "token",
)