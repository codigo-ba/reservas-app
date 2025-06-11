from django.middleware.csrf import get_token
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm
from .models import Turno

def pagina_inicio(request):
    return render(request, "inicio.html")

def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Loguea automáticamente después del registro
            return redirect("reservar_turno")  # Redirige a la página de reservas
    else:
        form = RegistroUsuarioForm()
    
    return render(request, "registro.html", {"form": form})


def iniciar_sesion(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Debes ingresar un nombre de usuario y contraseña.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # 🚀 Inicia sesión con el nuevo usuario
            
            response = HttpResponseRedirect(reverse("mis_turnos"))

            # 🚀 Regenerar y enviar la cookie CSRF
            response.set_cookie("csrftoken", get_token(request))

            messages.success(request, "Inicio de sesión exitoso.")
            return response
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
            return redirect("login")

    return render(request, "login.html")


@login_required
def reservar_turno(request):
    storage = get_messages(request)
    list(storage)  # Consume los mensajes previos para evitar acumulaciones inesperadas

    if request.method == "POST":
        fecha = request.POST.get("fecha", "").strip()
        hora = request.POST.get("hora", "").strip()

        if not fecha or not hora:
            messages.error(request, "Debes seleccionar una fecha y una hora válidas.")
            return redirect("reservar_turno")

        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de fecha u hora incorrecto. Intenta nuevamente.")
            return redirect("reservar_turno")

        ahora = datetime.now()
        turno_datetime = datetime.combine(fecha_obj, hora_obj)

        if fecha_obj == date.today() and turno_datetime < ahora:
            messages.error(request, "No puedes reservar turnos para horas que ya pasaron.")
            return redirect("reservar_turno")
        elif Turno.objects.filter(usuario=request.user, fecha=fecha_obj, hora=hora_obj).exists():
            messages.error(request, "Ya tienes un turno reservado en ese horario.")
            return redirect("reservar_turno")
        elif Turno.objects.filter(fecha=fecha_obj, hora=hora_obj).exists():
            messages.error(request, "Este turno ya está reservado. Por favor, elige otro horario.")
            return redirect("reservar_turno")
        else:
            Turno.objects.create(usuario=request.user, fecha=fecha_obj, hora=hora_obj, reservado=True)
            messages.success(request, "¡Turno reservado con éxito!")
            return redirect("mis_turnos")  # 🚀 Se mantiene estable sin expulsar al usuario

    turnos_ocupados = Turno.objects.filter(fecha=date.today()).values_list("hora", flat=True)
    horas_disponibles = ["09:00", "10:00", "11:00", "15:00", "16:00", "17:00", "18:00", "19:00"]

    response = render(request, "reserva.html", {"turnos_ocupados": turnos_ocupados, "horas_disponibles": horas_disponibles})

    # 🚀 Regenerar la cookie CSRF en cada solicitud de reserva
    response.set_cookie("csrftoken", get_token(request))

    return response



@login_required
def mis_turnos(request):
    storage = get_messages(request)
    list(storage)  # 🚀 Consume los mensajes previos para evitar acumulaciones inesperadas
    
    turnos = Turno.objects.filter(usuario=request.user, reservado=True)
    response = render(request, "mis_turnos.html", {"turnos": turnos})

    # 🚀 Forzar Django a enviar la cookie CSRF
    response.set_cookie("csrftoken", get_token(request))

    if request.method == "POST":
        turno_id = request.POST.get("turno_id")
        turno = Turno.objects.filter(id=turno_id, usuario=request.user)

        if turno.exists():
            turno.delete()
            messages.success(request, "Tu turno ha sido cancelado correctamente.")
            return JsonResponse({"success": True, "message": "Turno cancelado con éxito."})
        else:
            messages.error(request, "No se encontró el turno.")
            return JsonResponse({"success": False, "message": "Error al cancelar el turno."})
    return response

@login_required
def editar_turno(request, turno_id):
    storage = get_messages(request)
    list(storage)  # Consume los mensajes para que no se acumulen

    turno = get_object_or_404(Turno, id=turno_id, usuario=request.user)

    if request.method == "POST":
        fecha_nueva = request.POST.get("fecha")
        hora_nueva = request.POST.get("hora")

        if not fecha_nueva or not hora_nueva:
            messages.error(request, "Debes seleccionar una fecha y una hora válidas.")
            return redirect("editar_turno", turno_id=turno_id)

        try:
            fecha_obj = datetime.strptime(fecha_nueva, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora_nueva, "%H:%M").time()
        except ValueError:
            messages.error(request, "Formato de fecha u hora incorrecto. Intenta nuevamente.")
            return redirect("editar_turno", turno_id=turno_id)

        turno.fecha = fecha_obj
        turno.hora = hora_obj
        turno.save()
        messages.success(request, "Tu turno ha sido actualizado correctamente.")
        return redirect("mis_turnos")

    return render(request, "editar_turno.html", {"turno": turno})

@login_required
def cancelar_turno(request, turno_id):
    storage = get_messages(request)
    list(storage)  # Consume los mensajes para que no se acumulen

    turno = get_object_or_404(Turno, id=turno_id, usuario=request.user)

    if request.method == "POST":
        turno.delete()
        messages.success(request, "Tu turno ha sido cancelado correctamente.")
        return redirect("mis_turnos")

    return redirect("mis_turnos")

def cerrar_sesion(request):
    logout(request)  # 🚀 Cierra la sesión del usuario
    request.session.flush()  # 🚀 Borra todos los datos de sesión y CSRF
    request.session.clear()  
    response = redirect("login")
    response.delete_cookie("csrftoken")  # 🚀 Elimina cualquier token CSRF residual
    response.delete_cookie("sessionid")  # 🚀 Borra la cookie de sesión para prevenir problemas
    messages.success(request, "Has cerrado sesión correctamente.")
    return response
