from django.utils import timezone
from django.http import JsonResponse
from .models import Session, User

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = None
        auth_header = request.headers.get('Authorization')
        token = None

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = request.COOKIES.get('sessionid')

        if token:
            try:
                session = Session.objects.get(session_token=token)
                if not session.is_expired() and session.user.is_active:
                    request.user = session.user
            except (Session.DoesNotExist, ValueError):
                pass

        response = self.get_response(request)
        return response