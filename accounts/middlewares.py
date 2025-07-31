class BlockInactiveUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and not user.is_active:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Your account is inactive.")
        return self.get_response(request)

