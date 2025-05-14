from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registro, reservar_turno, mis_turnos, editar_turno, pagina_inicio, cancelar_turno

urlpatterns = [
    path("", pagina_inicio, name="inicio"),  # Página principal
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),
    path("reservar/", reservar_turno, name="reservar_turno"),
    path("mis_turnos/", mis_turnos, name="mis_turnos"),
    path("editar_turno/<int:turno_id>/", editar_turno, name="editar_turno"),
    path("cancelar_turno/<int:turno_id>/", cancelar_turno, name="cancelar_turno"),
]
