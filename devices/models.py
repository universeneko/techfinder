from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import django.utils.timezone

# devices/models.py

class Dispositivo(models.Model):
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=[('Móvil', 'Móvil'), ('Portátil', 'Portátil')])
    fecha_lanzamiento = models.DateField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # Nuevo campo
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Para almacenar el hash de la contraseña
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email


class Comentario(models.Model):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    dispositivo = models.ForeignKey("Dispositivo", on_delete=models.CASCADE)
    texto = models.TextField()
    calificacion = models.IntegerField()
    imagen = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Comentario de {self.usuario} sobre {self.dispositivo}"


class Compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    dispositivos = models.ManyToManyField(Dispositivo)
    fecha = models.DateTimeField(auto_now_add=True)
