from ninja import Router
from django.http import HttpRequest
from accounts.schemas import UserPostBody


router = Router(tags=['User'])


@router.post('/user')
def create_user(request: HttpRequest, data: UserPostBody):
    """"""

    print('************')
    print(dir(request.session))
    print('###')
    print(dir(request.user))
    print(data)
