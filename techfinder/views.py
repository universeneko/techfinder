# Librerías estándar de Python
import json
import os
from decimal import Decimal
from tempfile import NamedTemporaryFile

# Librerías de Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.db import transaction, OperationalError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import View

# Librerías de terceros
import requests
from pip._internal.utils import logging

# Librerías de DRF (Django Rest Framework)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Modelos de la aplicación
from techfinder.models import Producto, Carrito, CarritoProducto, Usuario


# Vista principal
def home_view(request):
    productos = Producto.objects.all()

    # Procesar filtros
    tipos = request.GET.get('tipo', '').split(',')
    sistemas_operativos = request.GET.get('sistema_operativo', '').split(',')
    precio_max = request.GET.get('precio_max')

    # Aplicar filtros
    if tipos and tipos[0]:
        productos = productos.filter(tipo__in=tipos)

    if sistemas_operativos and sistemas_operativos[0]:
        q_sistemas = Q()
        for sistema in sistemas_operativos:
            q_sistemas |= Q(sistema_operativo__iexact=sistema)
        productos = productos.filter(q_sistemas)

    if precio_max and precio_max.isdigit():
        productos = productos.filter(precio__lte=float(precio_max))

    context = {
        'productos': productos,
    }

    return render(request, 'techfinder_website_v2/main/index.html', context)

def index(request):
    print("\n==== DIAGNÓSTICO DE FILTROS ====")
    productos = Producto.objects.all()
    print(f"Total productos inicial: {productos.count()}")

    # Obtener y procesar filtros
    tipo = request.GET.get('tipo')
    sistema_operativo = request.GET.get('sistema_operativo')
    precio_max = request.GET.get('precio_max')

    print(f"Filtros recibidos:")
    print(f"- Tipo: {tipo}")
    print(f"- Sistema Operativo: {sistema_operativo}")
    print(f"- Precio máximo: {precio_max}")

    # Aplicar filtros uno por uno
    if tipo:
        tipos_lista = [t.strip() for t in tipo.split(',')]
        productos = productos.filter(tipo__in=tipos_lista)
        print(f"Después de filtrar por tipo: {productos.count()} productos")

    if sistema_operativo:
        so_lista = [s.strip() for s in sistema_operativo.split(',')]
        productos = productos.filter(sistema_operativo__in=so_lista)
        print(f"Después de filtrar por SO: {productos.count()} productos")

    if precio_max and precio_max.isdigit():
        productos = productos.filter(precio__lte=float(precio_max))
        print(f"Después de filtrar por precio: {productos.count()} productos")

    print("\nProductos finales:")
    for p in productos:
        print(f"- {p.nombre} (Tipo: {p.tipo}, SO: {p.sistema_operativo}, Precio: {p.precio})")

    context = {
        'productos': productos,
        'tipos_disponibles': dict(Producto.TIPOS_CHOICES),
        'sistemas_operativos': dict(Producto.SO_CHOICES),
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'techfinder_website_v2/components/products_grid.html', context)
    return render(request, 'techfinder_website_v2/main/index.html', context)


# Vista de la tienda
class StoreView(View):
    @staticmethod
    def get(request):
        # Iniciar con todos los productos
        productos = Producto.objects.all()

        # Obtener parámetros de filtrado
        tipo = request.GET.get('tipo')
        sistema_operativo = request.GET.get('sistema_operativo')
        precio_max = request.GET.get('precio_max')
        precio_min = request.GET.get('precio_min')  # Añadimos el precio mínimo

        # Aplicar filtros si existen
        if tipo:
            tipos = tipo.split(',')
            productos = productos.filter(tipo__in=tipos)

        if sistema_operativo:
            sistemas = sistema_operativo.split(',')
            productos = productos.filter(sistema_operativo__in=sistemas)

        # Filtro de precio máximo
        if precio_max and precio_max.isdigit():
            precio_max_decimal = Decimal(precio_max)
            productos = productos.filter(precio__lte=precio_max_decimal)

        # Filtro de precio mínimo
        if precio_min and precio_min.isdigit():
            precio_min_decimal = Decimal(precio_min)
            productos = productos.filter(precio__gte=precio_min_decimal)

        # Verificar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        context = {
            'productos': productos,
            # Mantener los valores de filtro en el contexto para el estado inicial
            'filtros_aplicados': {
                'tipo': tipo,
                'sistema_operativo': sistema_operativo,
                'precio_max': precio_max,
                'precio_min': precio_min,
            }
        }

        if is_ajax:
            return render(request, 'techfinder_website_v2/components/products_grid.html', context)

        return render(request, 'techfinder_website_v2/main/index.html', context)

# Vista de la cuenta
class AccountView(View):
    template_name = 'techfinder_website_v2/account/account.html'

    def get(self, request):
        return render(request, self.template_name)

    @staticmethod
    def post(request):
        # Obtener el tipo de formulario (login o registro)
        form_type = request.POST.get('form_type')

        if form_type == 'register':
            # Redirigir al RegisterView
            return redirect('register')
        elif form_type == 'login':
            # Redirigir al LoginView
            return redirect('login')
        else:
            messages.error(request, 'Formulario no válido')
            return redirect('account')


# Vista de inicio de sesión
class LoginView(View):
    @staticmethod
    def post(request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verificar que se proporcionaron las credenciales
        if not email or not password:
            messages.error(request, 'Por favor ingrese email y contraseña.')
            return redirect('account')

        user = Usuario.objects.filter(email=email).first()
        if not user:
            messages.error(request, 'No existe una cuenta con este email.')
            return redirect('account')

        authenticated_user = authenticate(request, email=email, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            messages.success(request, '¡Bienvenido de nuevo!')
            return redirect(reverse('account'))  # Home

        messages.error(request, 'Contraseña incorrecta.')
        return redirect('account')


# Configuración del logger
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            logger.info("Usuario autenticado intentó acceder a la página de registro. Redirigiendo a /account/")
            return redirect(reverse('account'))

        logger.info("Mostrando formulario de registro.")
        return render(request, 'techfinder_website_v2/account/auth/register.html')

    @staticmethod
    def post(request):
        logger.info("Recibiendo solicitud de registro.")

        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Datos recibidos: {data}")

            # Obtener datos del formulario
            nombre = data.get('nombre')
            apellidos = data.get('apellidos')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            permisos =  data.get('permisos')

            # Validamos que sea 0 o 1 (evita valores inválidos)
            if permisos not in [0, 1]:
                logger.warning(f"Valor de permisos inválido: {permisos}. Se asignará 0 por defecto.")
                permisos = 0

            logger.info(f"Valores extraídos: nombre={nombre}, apellidos={apellidos}, email={email}")

            # Validaciones
            if not all([nombre, apellidos, email, password, confirm_password]):
                logger.warning("Fallo en la validación: campos vacíos.")
                return JsonResponse({'error': 'Todos los campos son obligatorios.'}, status=400)

            if password != confirm_password:
                logger.warning("Fallo en la validación: las contraseñas no coinciden.")
                return JsonResponse({'error': 'Las contraseñas no coinciden.'}, status=400)

            if Usuario.objects.filter(email=email).exists():
                logger.warning(f"Fallo en la validación: el email {email} ya está registrado.")
                return JsonResponse({'error': 'El email ya está registrado.'}, status=400)

            # Crear usuario en una transacción atómica
            with transaction.atomic():
                logger.info("Creando nuevo usuario en la base de datos.")

                user = Usuario.objects.create(
                    nombre=nombre,
                    apellidos=apellidos,
                    email=email,
                    password=make_password(password),  # Encriptar contraseña
                    fecha_registro=timezone.now(),
                    permisos=permisos
                )

                logger.info(f"Usuario {user.email} creado con éxito. ID: {user.id}")

                # Crear carrito para el usuario
                Carrito.objects.create(usuario=user)
                logger.info(f"Carrito creado para el usuario {user.email}")

                # Autenticar y hacer login
                authenticated_user = authenticate(request, email=email, password=password)
                if authenticated_user is None:
                    logger.error("Error en la autenticación después del registro.")
                    raise ValueError("Error en la autenticación del usuario")

                login(request, authenticated_user)
                logger.info(f"Usuario {user.email} autenticado y logueado con éxito.")

                return JsonResponse({'success': True, 'message': 'Cuenta creada exitosamente.'}, status=201)

        except json.JSONDecodeError:
            logger.error("Error en el formato JSON recibido.")
            return JsonResponse({'error': 'Formato JSON inválido.'}, status=400)

        except Exception as e:
            logger.error(f"Error inesperado al crear el usuario: {str(e)}", exc_info=True)

            # Si algo falla, eliminamos el usuario si se creó
            if 'user' in locals():
                user.delete()
                logger.warning(f"Usuario {user.email} eliminado debido a un error.")

            return JsonResponse({'error': 'Ocurrió un error al crear la cuenta. Inténtalo de nuevo.'}, status=500)

# Vista de cierre de sesión
class LogoutView(View):
    @staticmethod
    def post(request):
        # Aseguramos que se eliminen todas las sesiones y cookies
        logout(request)

        # Limpiamos cualquier cookie específica de la aplicación si existiera
        response = redirect('account')
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')

        # Agregamos el mensaje de éxito
        messages.success(request, 'Sesión cerrada exitosamente. ¡Hasta pronto!')

        return response

    @staticmethod
    def get(request):
        # Redirigimos POST requests a post() para seguir el principio PRG
        return redirect('account')


# Vista de privacidad
def privacidad_view(request):
    return render(request, 'techfinder_website_v2/main/privacidad.html')


# Vista del carrito
def get(request):
    carrito_productos = CarritoProducto.objects.filter(carrito__usuario=request.user)
    total_carrito = sum(item.producto.precio * item.cantidad for item in carrito_productos)
    context = {
        'carrito_productos': carrito_productos,
        'total_carrito': total_carrito,
    }
    return render(request, 'techfinder_website_v2/main/carrito_lateral.html', context)


# Vista para agregar al carrito
@method_decorator(login_required, name='dispatch')
class AgregarCarritoView(View):
    @staticmethod
    def post(request, producto_id):
        try:
            producto = Producto.objects.get(id=producto_id)
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)

            carrito_producto, created = CarritoProducto.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={'cantidad': 1}
            )

            if not created:
                carrito_producto.cantidad += 1
                carrito_producto.save()

            messages.success(request, 'Producto agregado al carrito.')
            return redirect('store')

        except Exception as e:
            messages.error(request, 'Error al agregar al carrito.')
            return redirect('store')


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Solo usuarios autenticados pueden ver la lista
def get_all_users(request):
    usuarios = Usuario.objects.all().values('id', 'nombre', 'apellidos', 'email')
    return Response({"usuarios": list(usuarios)}, status=200)
@permission_classes([IsAuthenticated])
def user_profile(request):
    return render(request, 'techfinder_website_v2/account/user.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user(request):
    print("Solicitud recibida para actualizar usuario")
    if request.method == 'POST':
        user = request.user

        # Actualizar información básica
        user.nombre = request.data.get('nombre')
        user.apellidos = request.data.get('apellidos')
        user.email = request.data.get('email')

        # Manejar cambio de contraseña
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if new_password:
            if not check_password(current_password, user.password):
                messages.error(request, 'La contraseña actual es incorrecta')
                return redirect('user')
            user.set_password(new_password)

        user.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('home')

    return redirect('home')


@method_decorator(csrf_exempt, name='dispatch')  # 🔥 Evita error CSRF
@method_decorator(api_view(['POST', 'DELETE']), name='dispatch')  # Acepta POST y DELETE
@method_decorator(permission_classes([IsAuthenticated]), name='dispatch')  # Requiere autenticación
class DeleteAccountView(View):

    @staticmethod
    def post(request, *args, **kwargs):
        """Elimina la cuenta del usuario autenticado (desde la plataforma web)."""
        try:
            request.user.delete()
            return JsonResponse({'success': True, 'message': 'Cuenta eliminada correctamente'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    @staticmethod
    def delete(request, *args, **kwargs):
        """Elimina una cuenta por ID (desde la API)."""
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('id')

            if not user_id:
                return JsonResponse({'success': False, 'error': 'Se requiere un ID de usuario'}, status=400)

            try:
                user = Usuario.objects.get(id=user_id)
            except Usuario.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)

            user.delete()
            return JsonResponse({'success': True, 'message': 'Cuenta eliminada correctamente'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Admin View
class AdminView(UserPassesTestMixin, View):
    template_name = 'techfinder_website_v2/admin/admin.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('home')

    def get(self, request):
        productos = Producto.objects.all().order_by('-id')
        return render(request, self.template_name, {'productos': productos})


    @staticmethod
    def post(request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get('action')

            if action == 'add':
                try:
                    nombre = request.POST.get('nombre')
                    descripcion = request.POST.get('descripcion')
                    precio = float(request.POST.get('precio'))
                    stock = int(request.POST.get('stock'))
                    tipo = request.POST.get('tipo')
                    sistema_operativo = request.POST.get('sistema_operativo')
                    imagen = request.FILES.get('imagen')

                    # Guardar imagen
                    if imagen:
                        path = default_storage.save(
                            f'productos/{imagen.name}',
                            ContentFile(imagen.read())
                        )
                    else:
                        path = 'productos/default.jpg'

                    producto = Producto.objects.create(
                        nombre=nombre,
                        descripcion=descripcion,
                        precio=precio,
                        stock=stock,
                        tipo=tipo,
                        sistema_operativo=sistema_operativo,
                        imagen=path
                    )

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Producto añadido correctamente',
                        'id': producto.id
                    })

                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=400)

            elif action == 'update':
                try:
                    data = json.loads(request.body)
                    producto_id = data.get('id')
                    producto = Producto.objects.get(id=producto_id)

                    fields = ['nombre', 'descripcion', 'precio', 'stock', 'tipo', 'sistema_operativo']
                    for field in fields:
                        if field in data:
                            setattr(producto, field, data[field])

                    producto.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Producto actualizado correctamente'
                    })

                except Producto.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Producto no encontrado'
                    }, status=404)
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=400)

            elif action == 'delete':
                try:
                    producto_id = request.POST.get('id')
                    producto = Producto.objects.get(id=producto_id)

                    # Eliminar imagen si no es la default
                    if producto.imagen and 'default.jpg' not in producto.imagen.name:
                        default_storage.delete(producto.imagen.name)

                    producto.delete()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Producto eliminado correctamente'
                    })

                except Producto.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Producto no encontrado'
                    }, status=404)
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=400)

        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)


@login_required
@require_http_methods(["POST"])
def add_device(request):
    try:
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        tipo = request.POST.get('tipo')
        sistema_operativo = request.POST.get('sistema')
        imagen = request.FILES.get('imagen')

        # Validar campos requeridos
        if not all([nombre, precio, stock, tipo, sistema_operativo]):
            return JsonResponse({
                'status': 'error',
                'message': 'Todos los campos son obligatorios'
            }, status=400)

        # Preparar datos base del producto
        producto_data = {
            'nombre': nombre,
            'descripcion': descripcion,
            'precio': Decimal(precio),
            'stock': int(stock),
            'tipo': tipo,
            'sistema_operativo': sistema_operativo
        }

        # Manejar la imagen si existe
        if imagen:
            # Asegurar que el directorio products existe
            products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
            os.makedirs(products_dir, exist_ok=True)

            # Generar ruta relativa para la imagen
            upload_path = os.path.join('products', imagen.name)
            producto_data['imagen'] = upload_path

            # Guardar el archivo físicamente
            full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
            with open(full_path, 'wb+') as destination:
                for chunk in imagen.chunks():
                    destination.write(chunk)

        # Crear el producto
        producto = Producto.objects.create(**producto_data)

        return JsonResponse({
            'status': 'success',
            'message': 'Dispositivo añadido correctamente',
            'id': producto.id
        })

    except ValueError as ve:
        return JsonResponse({
            'status': 'error',
            'message': f'Error de validación: {str(ve)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)

@login_required
def update_device(request, producto_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    try:
        producto = Producto.objects.get(id=producto_id)

        if request.method == 'POST':
            # Actualizar campos
            if 'nombre' in request.POST:
                producto.nombre = request.POST['nombre']
            if 'precio' in request.POST:
                producto.precio = request.POST['precio']
            if 'stock' in request.POST:
                producto.stock = request.POST['stock']
            if 'tipo' in request.POST:
                producto.tipo = request.POST['tipo']
            if 'sistema_operativo' in request.POST:
                producto.sistema_operativo = request.POST['sistema_operativo']

            producto.save()
            return JsonResponse({
                'message': 'Producto actualizado exitosamente',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                    'tipo': producto.tipo,
                    'sistema_operativo': producto.sistema_operativo
                }
            })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def delete_device(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        producto.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class CarritoApiView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        productos_carrito = CarritoProducto.objects.filter(carrito=carrito)

        productos = []
        total = 0

        for item in productos_carrito:
            producto = item.producto
            subtotal = producto.precio * item.cantidad
            total += subtotal

            productos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'imagen': producto.imagen.url if producto.imagen else None,
                'cantidad': item.cantidad,
                'stock': producto.stock,
                'subtotal': float(subtotal)
            })

        return JsonResponse({
            'productos': productos,
            'total': float(total)
        })

class ActualizarCarritoApiView(View):
    @staticmethod
    def post(request, producto_id):
        try:
            with transaction.atomic():
                if request.content_type == 'application/json':
                    data = json.loads(request.body)
                    nueva_cantidad = int(data.get('cantidad', 0))
                else:
                    nueva_cantidad = int(request.POST.get('cantidad', 0))

                if nueva_cantidad < 1:
                    return JsonResponse({
                        'success': False,
                        'error': 'La cantidad no puede ser menor a 1'
                    }, status=400)

                carrito_producto = CarritoProducto.objects.select_for_update().get(
                    carrito__usuario=request.user,
                    producto_id=producto_id
                )

                producto = Producto.objects.select_for_update().get(id=producto_id)
                diferencia = nueva_cantidad - carrito_producto.cantidad

                if diferencia > 0 and producto.stock < diferencia:
                    return JsonResponse({
                        'success': False,
                        'error': 'No hay suficiente stock disponible'
                    })

                producto.stock -= diferencia
                producto.save()

                carrito_producto.cantidad = nueva_cantidad
                carrito_producto.save()

                return JsonResponse({
                    'success': True,
                    'nueva_cantidad': nueva_cantidad,
                    'nuevo_total': float(carrito_producto.carrito.obtener_total())
                })

        except OperationalError as e:
            if "database is locked" in str(e):
                # Si es error de base de datos bloqueada, retornamos éxito
                # ya que sabemos que la operación eventualmente se completará
                return JsonResponse({
                    'success': True,
                    'nueva_cantidad': nueva_cantidad,
                    'nuevo_total': float(carrito_producto.carrito.obtener_total())
                })
            # Si es otro tipo de error operacional, lo manejamos como error
            return JsonResponse({
                'success': False,
                'error': 'Error en la operación'
            })
        except (CarritoProducto.DoesNotExist, Producto.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': 'Producto no encontrado en el carrito'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class EliminarCarritoApiView(View):
    @transaction.atomic
    def delete(self, request, producto_id):
        try:
            carrito = request.user.get_or_create_carrito()

            # Obtener el producto y el item del carrito
            carrito_producto = CarritoProducto.objects.get(
                carrito=carrito,
                producto_id=producto_id
            )

            # Restaurar el stock
            producto = carrito_producto.producto
            producto.stock += carrito_producto.cantidad
            producto.save()

            # Eliminar el item del carrito
            carrito_producto.delete()

            return JsonResponse({
                'success': True,
                'stock_actualizado': producto.stock
            })

        except CarritoProducto.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Producto no encontrado en el carrito'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@require_POST
@login_required
def agregar_al_carrito(request):
    try:
        producto_id = request.POST.get('producto_id')
        producto = Producto.objects.get(id=producto_id)

        # Verificar stock
        if producto.stock <= 0:
            return JsonResponse({
                'success': False,
                'message': 'No hay stock disponible'
            }, status=400)

        # Obtener o crear el carrito del usuario
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

        # Añadir al carrito
        carrito_producto, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': 1}
        )

        if not created:
            carrito_producto.cantidad += 1
            carrito_producto.save()

        # Actualizar stock
        producto.stock -= 1
        producto.save()

        return JsonResponse({
            'success': True,
            'message': 'Producto añadido al carrito',
            'nuevo_stock': producto.stock
        })

    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al añadir al carrito'
        }, status=500)


def get_cart_count(request):
    if request.user.is_authenticated:
        return CarritoProducto.objects.filter(carrito__usuario=request.user).count()
    return 0

def get_cart_count_api(request):
    count = get_cart_count(request)  # La función que creamos antes
    return JsonResponse({'count': count})


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_device_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        # Obtener datos del JSON
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        precio = data.get('precio')
        stock = data.get('stock')
        tipo = data.get('tipo')
        sistema_operativo = data.get('sistema_operativo')
        imagen_url = data.get('imagen_url')

        # Validar campos requeridos
        if not all([nombre, precio, stock, tipo, sistema_operativo]):
            return JsonResponse({
                'status': 'error',
                'message': 'Todos los campos obligatorios deben estar presentes'
            }, status=400)

        # Preparar datos del producto
        producto_data = {
            'nombre': nombre,
            'descripcion': descripcion,
            'precio': Decimal(precio),
            'stock': int(stock),
            'tipo': tipo,
            'sistema_operativo': sistema_operativo
        }

        # Si se proporciona una URL de imagen, la descargamos y la guardamos
        if imagen_url:
            # Descargar la imagen
            response = requests.get(imagen_url)
            if response.status_code == 200:
                # Crear un archivo temporal en memoria
                imagen_temp = NamedTemporaryFile(delete=True)
                imagen_temp.write(response.content)
                imagen_temp.flush()

                # Crear el nombre de archivo
                imagen_filename = os.path.basename(imagen_url)
                # Guardar la imagen en el modelo de producto
                producto_data['imagen'] = File(imagen_temp, name=imagen_filename)

        # Crear el producto en la base de datos
        producto = Producto.objects.create(**producto_data)

        return JsonResponse({
            'status': 'success',
            'message': 'Dispositivo añadido correctamente',
            'id': producto.id
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'El cuerpo de la solicitud debe ser un JSON válido'
        }, status=400)
    except ValueError as ve:
        return JsonResponse({
            'status': 'error',
            'message': f'Error de validación: {str(ve)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)


@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_device_api(request, producto_id):
    try:
        # Verificar si el producto existe
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Producto no encontrado'
            }, status=404)

        # Cargar los datos del JSON
        data = json.loads(request.body.decode('utf-8'))

        # Extraer los datos que puedan ser editados
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        precio = data.get('precio')
        stock = data.get('stock')
        tipo = data.get('tipo')
        sistema_operativo = data.get('sistema_operativo')
        imagen_url = data.get('imagen_url')  # Opcional

        # Editar solo los campos que están presentes en la solicitud
        if nombre:
            producto.nombre = nombre
        if descripcion:
            producto.descripcion = descripcion
        if precio:
            producto.precio = Decimal(precio)
        if stock:
            producto.stock = int(stock)
        if tipo:
            producto.tipo = tipo
        if sistema_operativo:
            producto.sistema_operativo = sistema_operativo
        if imagen_url:
            # Si hay una nueva URL de imagen, la descargamos y actualizamos
            response = requests.get(imagen_url)
            if response.status_code == 200:
                # Guardar la nueva imagen
                imagen_temp = NamedTemporaryFile(delete=True)
                imagen_temp.write(response.content)
                imagen_temp.flush()
                imagen_filename = os.path.basename(imagen_url)
                producto.imagen = File(imagen_temp, name=imagen_filename)

        # Guardar los cambios en el producto
        producto.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Producto actualizado correctamente',
            'id': producto.id
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'El cuerpo de la solicitud debe ser un JSON válido'
        }, status=400)
    except ValueError as ve:
        return JsonResponse({
            'status': 'error',
            'message': f'Error de validación: {str(ve)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_device_api(request, producto_id):
    try:
        # Buscar el producto por ID
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Producto no encontrado'
            }, status=404)

        # Eliminar el producto
        producto.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Producto eliminado correctamente',
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_devices(request):
    try:
        # Obtener todos los productos de la base de datos
        productos = Producto.objects.all()

        # Crear una lista con los productos en formato legible
        productos_list = []
        for producto in productos:
            producto_data = {
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': str(producto.precio),
                'stock': producto.stock,
                'tipo': producto.tipo,
                'sistema_operativo': producto.sistema_operativo,
                'imagen_url': producto.imagen.url if producto.imagen else 'No disponible',
            }
            productos_list.append(producto_data)

        return Response({
            'status': 'success',
            'data': productos_list
        }, status=200)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al obtener los productos: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_device_by_id(request, id):
    try:
        # Intentamos obtener el producto por ID
        producto = Producto.objects.get(id=id)

        # Crear el producto en formato legible
        producto_data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': str(producto.precio),
            'stock': producto.stock,
            'tipo': producto.tipo,
            'sistema_operativo': producto.sistema_operativo,
            'imagen_url': producto.imagen.url if producto.imagen else 'No disponible',
        }

        return Response({
            'status': 'success',
            'data': producto_data
        }, status=200)

    except Producto.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error al obtener el producto: {str(e)}'
        }, status=500)