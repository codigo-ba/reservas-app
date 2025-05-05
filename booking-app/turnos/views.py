from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuarioForm


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
    # Lógica de reservas de turnos
    pass



