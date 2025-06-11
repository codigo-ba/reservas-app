from django.urls import path
from django.contrib.auth import views as auth_views
from .views import pagina_inicio, registro, iniciar_sesion, reservar_turno, mis_turnos, editar_turno, cancelar_turno, cerrar_sesion

urlpatterns = [
    path("", pagina_inicio, name="inicio"),  # Página principal
    path("login/", iniciar_sesion, name="login"),  # 🚀 Nueva ruta para iniciar sesión
    path("logout/", cerrar_sesion, name="logout"),
    path('registro/', registro, name='registro'),
    path("reservar/", reservar_turno, name="reservar_turno"),
    path("mis_turnos/", mis_turnos, name="mis_turnos"),
    path("editar_turno/<int:turno_id>/", editar_turno, name="editar_turno"),
    path("cancelar_turno/<int:turno_id>/", cancelar_turno, name="cancelar_turno"),
]
