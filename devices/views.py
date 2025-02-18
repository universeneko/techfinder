import re
from functools import wraps
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Dispositivo, Compra
from django.contrib.auth.decorators import login_required
from backend import settings
from .models import Dispositivo
from .models import Usuario
from .serializers import DispositivoSerializer


def home(request):
    return render(request, "home.html")


def shop(request):
    dispositivos = Dispositivo.objects.all()
    filtros_aplicados = False

    # Filtros
    tipo = request.GET.get('tipo')
    marca = request.GET.get('marca')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    sort_by = request.GET.get('sort_by')

    # Verificar si se aplicó algún filtro
    if tipo or marca or precio_min or precio_max:
        filtros_aplicados = True

    # Aplicar filtros
    if tipo:
        dispositivos = dispositivos.filter(tipo=tipo)
    if marca:
        dispositivos = dispositivos.filter(marca=marca)

    # Filtrado por rango de precios
    if precio_min:
        try:
            precio_min = float(precio_min)
            dispositivos = dispositivos.filter(precio__gte=precio_min)
        except ValueError:
            pass

    if precio_max:
        try:
            precio_max = float(precio_max)
            dispositivos = dispositivos.filter(precio__lte=precio_max)
        except ValueError:
            pass

    if request.GET.get('con_stock'):
        dispositivos = dispositivos.filter(stock__gt=0)

    # Aplicar ordenamiento
    if sort_by == 'price_asc':
        dispositivos = dispositivos.order_by('precio')
    elif sort_by == 'price_desc':
        dispositivos = dispositivos.order_by('-precio')
    elif sort_by == 'rating_desc':
        dispositivos = dispositivos.order_by('-rating')

    context = {
        'dispositivos': dispositivos,
        'filtros_aplicados': filtros_aplicados,
        'total_dispositivos': dispositivos.count()
    }



    return render(request, 'shop.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Cambiado de 'email' a 'username'
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Por favor complete todos los campos'
            })

        try:
            usuario = Usuario.objects.get(email=username)  # Asumiendo que username es el email
            if usuario.check_password(password):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_email'] = usuario.email

                return JsonResponse({
                    'success': True,
                    'user': {
                        'name': usuario.nombre,
                        'email': usuario.email
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Contraseña incorrecta'
                })
        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No existe un usuario con ese email'
            })

    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        if request.method == 'POST':
            print("Datos recibidos:", request.POST)
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validación inicial mejorada
        if not all([name, email, password]):
            return JsonResponse({
                'success': False,
                'error': 'Por favor complete todos los campos'
            })

        try:

            # Validar formato de email
            email_validator = EmailValidator()
            email_validator(email)

            # Verificar si el usuario ya existe
            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Este email ya está registrado'
                })

            # Validar longitud de la contraseña
            if len(password) < 8:
                return JsonResponse({
                    'success': False,
                    'error': 'La contraseña debe tener al menos 8 caracteres'
                })

            # Crear usuario
            usuario = Usuario(
                nombre=name,
                email=email
            )
            usuario.set_password(password)
            usuario.save()

            return JsonResponse({
                'success': True,
                'message': '¡Registro exitoso! Por favor inicia sesión.'
            })

        except ValidationError:
            return JsonResponse({
                'success': False,
                'error': 'Por favor ingrese un email válido'
            })
        except Exception:
            return JsonResponse({
                'success': False,
                'error': 'Error en el registro. Por favor intente nuevamente'
            })

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return JsonResponse({
        'success': True,
        'message': '¡Sesión cerrada exitosamente!'
    })



def manage(request):
    return render(request, "manage.html")

def admin_panel(request):
    return render(request, "admin.html")

class ProductList(APIView):
    @staticmethod
    def get(request):
        dispositivos = Dispositivo.objects.all()
        serializer = DispositivoSerializer(dispositivos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def login_required_except_paths(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Obtener la ruta actual
        current_path = request.path_info

        # Verificar si la ruta actual está en las excepciones
        for path in settings.LOGIN_REQUIRED_IGNORE_PATHS:
            if re.match(path, current_path):
                return view_func(request, *args, **kwargs)

        # Si no está en las excepciones, verificar si está autenticado
        if 'usuario_id' not in request.session:
            # Aquí puedes decidir si redirigir al login o permitir vista limitada
            return view_func(request, *args, **kwargs)  # Permite vista de invitado

        return view_func(request, *args, **kwargs)

    return _wrapped_view

@login_required_except_paths
def tu_vista(request):

    pass

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def guest_login(request):
    try:
        # Log para debugging
        logger.info(f"Método de la petición: {request.method}")
        logger.info(f"Headers: {request.headers}")

        # Establecer la sesión de invitado
        request.session['is_guest'] = True
        request.session.pop('usuario_id', None)
        request.session.pop('usuario_email', None)
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': 'Sesión de invitado iniciada correctamente'
        })
    except Exception as e:
        logger.error(f"Error en guest_login: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required(login_url='/login/')  # Especificamos la URL de login directamente
def add_to_cart(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id)

    # Verificar si hay stock disponible
    if dispositivo.stock <= 0:
        messages.error(request, 'Lo sentimos, no hay stock disponible.')
        return redirect('shop')

    # Obtener o crear una compra para el usuario
    compra, created = Compra.objects.get_or_create(
        usuario_id=request.session['usuario_id'],
        defaults={'usuario_id': request.session['usuario_id']}
    )

    # Añadir el dispositivo a la compra
    compra.dispositivos.add(dispositivo)

    # Reducir el stock
    dispositivo.stock -= 1
    dispositivo.save()

    messages.success(request, 'Producto añadido al carrito correctamente.')
    return redirect('cart')


@login_required(login_url='/login/')  # También añadirlo aquí
def cart_view(request):
    try:
        compra = Compra.objects.get(usuario_id=request.session['usuario_id'])
        dispositivos = compra.dispositivos.all()
    except Compra.DoesNotExist:
        dispositivos = []

    return render(request, 'cart.html', {'dispositivos': dispositivos})
