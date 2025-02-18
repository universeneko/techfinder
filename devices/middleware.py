from django.shortcuts import redirect
from django.urls import reverse


class SessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs que no requieren autenticación
        public_urls = ['/login/', '/register/']

        if not request.path in public_urls and not request.session.get('usuario_id'):
            return redirect('login')

        response = self.get_response(request)
        return response
