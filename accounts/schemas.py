from ninja import Schema


class UserPostBody(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str
    organization: str = None
