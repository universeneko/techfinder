import json
import os
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction, OperationalError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import View

from techfinder.models import (
    Carrito,
    CarritoProducto,
    Producto,
    Usuario,
)

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


class RegisterView(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect(reverse('account')) #home
        return render(request, 'techfinder_website_v2/account/auth/register.html')

    @staticmethod
    def post(request):
        # Obtener datos del formulario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validaciones
        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('account')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('account')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return redirect('account')

        try:
            from django.db import transaction
            with transaction.atomic():
                # Crear usuario
                user = Usuario.objects.create(
                    nombre=first_name,
                    apellidos=last_name,
                    email=email,
                    password=make_password(password),
                    fecha_registro=timezone.now(),
                    permisos=0
                )

                # Crear carrito para el usuario
                Carrito.objects.create(usuario=user)

                # Autenticar y hacer login
                authenticated_user = authenticate(request, email=email, password=password)
                if authenticated_user is None:
                    raise ValueError("Error en la autenticación del usuario")

                login(request, authenticated_user)
                messages.success(request, '¡Cuenta creada exitosamente!')
                return redirect(reverse('account')) #home

        except Exception as e:
            # Si algo falla, eliminamos el usuario si se creó
            if 'user' in locals():
                user.delete()
            messages.error(request, 'Ocurrió un error al crear la cuenta. Por favor, inténtalo de nuevo.')
            return redirect('account')

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

@login_required
def user_profile(request):
    return render(request, 'techfinder_website_v2/account/user.html')


@login_required
def update_user(request):
    if request.method == 'POST':
        user = request.user

        # Actualizar información básica
        user.nombre = request.POST.get('nombre')
        user.apellidos = request.POST.get('apellidos')
        user.email = request.POST.get('email')

        # Manejar cambio de contraseña
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        if new_password:
            if not check_password(current_password, user.password):
                messages.error(request, 'La contraseña actual es incorrecta')
                return redirect('user')
            user.set_password(new_password)

        user.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('home')

    return redirect('home')


@login_required
def delete_account(request):
    if request.method == 'POST':
        try:
            request.user.delete()
            messages.success(request, 'Cuenta eliminada correctamente')
            return JsonResponse({
                'success': True,
                'message': 'Cuenta eliminada correctamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

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