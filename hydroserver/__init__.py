from functools import lru_cache
from authlib.integrations.django_client import OAuth
from pydantic import BaseSettings, HttpUrl
from hydroserver.settings import AUTHLIB_OAUTH_CLIENTS, OUTSIDE_HOST

orcid_client = AUTHLIB_OAUTH_CLIENTS['orcid']

class Settings(BaseSettings):
    orcid_client_id: str = orcid_client['client_id']
    orcid_client_secret: str = orcid_client['client_secret']
    orcid_authorize_url: HttpUrl = orcid_client['authorize_url']
    # orcid_token_url: HttpUrl = orcid_client['access_token_url']
    # orcid_health_url: HttpUrl = orcid_client['health_url']

    outside_host: str = OUTSIDE_HOST

    @property
    def local_development(self):
        return self.outside_host == "localhost:8000"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
oauth = OAuth()
oauth.register(
    name='orcid',
    client_kwargs={'scope': 'openid email profile'},
    response_type= "token",
)