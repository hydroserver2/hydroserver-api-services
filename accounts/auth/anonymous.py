def anonymous_auth(request):

    request.authenticated_user = None

    return True
