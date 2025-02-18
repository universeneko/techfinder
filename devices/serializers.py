from rest_framework import serializers
from .models import Dispositivo

class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = ['id', 'nombre', 'marca', 'tipo', 'fecha_lanzamiento', 'precio']
