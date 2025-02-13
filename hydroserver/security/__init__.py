from .anonymous import anonymous_auth
from .basic import BasicAuth
from .session import SessionAuth
from .bearer import BearerAuth

basic_auth = BasicAuth()
session_auth = SessionAuth(csrf=True)
bearer_auth = BearerAuth()
