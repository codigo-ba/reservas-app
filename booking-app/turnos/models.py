from django.db import models
from django.contrib.auth.models import User

class Turno(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    reservado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario} - {self.fecha} {self.hora}"


