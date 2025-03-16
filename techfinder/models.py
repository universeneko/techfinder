from django.contrib.auth.models import (AbstractUser,
                                        AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin
                                        )
from django.db import models
import uuid

# Modelo Usuario
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    permisos = models.IntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellidos']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    def get_full_name(self):
        return f"{self.nombre} {self.apellidos}"

    def get_short_name(self):
        return self.nombre

    def get_or_create_carrito(self):
        """
        Obtiene el carrito activo del usuario o crea uno nuevo si no existe
        """
        # Utilizamos el relacionador inverso para acceder a los carritos
        carritos = self.carrito_set.filter(estado='activo')

        if carritos.exists():
            return carritos.first()

        # Si no existe un carrito activo, creamos uno nuevo
        return self.carrito_set.create(estado='activo')

# Modelo de Producto
class Producto(models.Model):
    TIPOS_CHOICES = [
        ('Laptop', 'Laptops'),
        ('Computador Torre', 'Computadores Torre'),
        ('Smartphone', 'Smartphones'),
        ('Smartwatch', 'Relojes Inteligentes'),
        ('Tablet', 'Tablets')
    ]

    SO_CHOICES = [
        ('Windows', 'Windows'),
        ('MacOS', 'MacOS'),
        ('Linux', 'Linux'),
        ('Android', 'Android'),
        ('iOS', 'iOS')
    ]

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.FileField(upload_to='products/', null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    stock = models.IntegerField()
    tipo = models.CharField(max_length=100, choices=TIPOS_CHOICES)
    sistema_operativo = models.CharField(max_length=100, choices=SO_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo de Compra
class Compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra {self.id} de {self.usuario.nombre}"

# Modelo de Carrito
class Carrito(models.Model):
    # usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, default='activo')

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"

    def obtener_total(self):
        total = 0
        productos_carrito = self.carritoproducto_set.all()  # Obtiene todos los CarritoProducto relacionados

        for item in productos_carrito:
            subtotal = item.producto.precio * item.cantidad
            total += subtotal

        return float(total)

# Modelo intermedio para Carrito_Producto
class CarritoProducto(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

# Modelo intermedio para Detalle_Compra
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

# Modelo de Comentario
class Comentario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    texto = models.TextField()
    calificacion = models.DecimalField(max_digits=2, decimal_places=1)
    fecha = models.DateTimeField(auto_now_add=True)
