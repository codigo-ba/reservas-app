from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login
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


@login_required
def reservar_turno(request):
    # 🚀 Limpiar mensajes previos antes de agregar nuevos
    storage = get_messages(request)
    list(storage)  # Consume los mensajes para que no se acumulen

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
        else:
            Turno.objects.create(usuario=request.user, fecha=fecha_obj, hora=hora_obj, reservado=True)
            messages.success(request, "¡Turno reservado con éxito!")
            return redirect("mis_turnos")

    return render(request, "reserva.html")


@login_required
def mis_turnos(request):
    turnos = Turno.objects.filter(usuario=request.user, reservado=True)

    if request.method == "POST":
        turno_id = request.POST.get("turno_id")
        Turno.objects.filter(id=turno_id, usuario=request.user).delete()
        return redirect("mis_turnos")

    return render(request, "mis_turnos.html", {"turnos": turnos})

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





