from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm
from .models import Turno


def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Loguea automáticamente después del registro
            return redirect('/')
    else:
        form = RegistroUsuarioForm()
    return render(request, "registro.html", {"form": form})

@login_required
def reservar_turno(request):
    if request.method == "POST":
        fecha = request.POST.get("fecha", "").strip()  # Elimina espacios extra
        hora = request.POST.get("hora", "").strip()  

        # Validar si se ingresaron fecha y hora
        if not fecha or not hora:
            mensaje = "Debes seleccionar una fecha y una hora válidas."
            return render(request, "reserva.html", {"mensaje": mensaje})

        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora, "%H:%M").time()
        except ValueError:
            mensaje = "Formato de fecha u hora incorrecto. Intenta nuevamente."
            return render(request, "reserva.html", {"mensaje": mensaje})

        # Obtener la fecha y hora actual
        ahora = datetime.now()
        turno_datetime = datetime.combine(fecha_obj, hora_obj)

        # Validar que no se pueda reservar en horas pasadas si la fecha es hoy
        if fecha_obj == date.today() and turno_datetime < ahora:
            mensaje = "No puedes reservar turnos para horas que ya pasaron."
        elif Turno.objects.filter(usuario=request.user, fecha=fecha_obj, hora=hora_obj).exists():
            mensaje = "Ya tienes un turno reservado en ese horario."
        else:
            Turno.objects.create(usuario=request.user, fecha=fecha_obj, hora=hora_obj, reservado=True)
            mensaje = "Turno reservado con éxito."

        return render(request, "reserva.html", {"mensaje": mensaje})

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
    turno = get_object_or_404(Turno, id=turno_id, usuario=request.user)

    if request.method == "POST":
        fecha_nueva = request.POST.get("fecha")
        hora_nueva = request.POST.get("hora")

        # Validar que la nueva fecha y hora no estén vacías
        if not fecha_nueva or not hora_nueva:
            mensaje = "Debes seleccionar una fecha y una hora válidas."
            return render(request, "editar_turno.html", {"turno": turno, "mensaje": mensaje})

        try:
            fecha_obj = datetime.strptime(fecha_nueva, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora_nueva, "%H:%M").time()
        except ValueError:
            mensaje = "Formato de fecha u hora incorrecto. Intenta nuevamente."
            return render(request, "editar_turno.html", {"turno": turno, "mensaje": mensaje})

        # Validar que la nueva hora no sea anterior a la actual si la fecha es hoy
        ahora = datetime.now()
        nuevo_turno_datetime = datetime.combine(fecha_obj, hora_obj)

        if fecha_obj == date.today() and nuevo_turno_datetime < ahora:
            mensaje = "No puedes cambiar el turno a una hora que ya pasó."
        elif Turno.objects.filter(usuario=request.user, fecha=fecha_obj, hora=hora_obj).exists():
            mensaje = "Ya tienes un turno reservado en ese horario."
        else:
            turno.fecha = fecha_obj
            turno.hora = hora_obj
            turno.save()
            return redirect("mis_turnos")

        return render(request, "editar_turno.html", {"turno": turno, "mensaje": mensaje})

    return render(request, "editar_turno.html", {"turno": turno})



