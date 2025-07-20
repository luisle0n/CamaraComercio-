from django.shortcuts import redirect
from django.urls import reverse

class ForzarCambioContrasenaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'debe_cambiar_contrasena', False):
            if request.path not in [reverse('cambio_obligatorio_contrasena'), reverse('logout')]:
                return redirect('cambio_obligatorio_contrasena')
        return self.get_response(request)
