document.addEventListener("DOMContentLoaded", function () {
    // Inicializar Flatpickr con validación de fechas
    flatpickr("#datepicker", {
        minDate: "today", // Evita selección de fechas anteriores
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
            validarFecha(dateStr);
        }
    });
});

// Función para validar la fecha seleccionada
function validarFecha(fechaSeleccionada) {
    const hoy = new Date().toISOString().split("T")[0]; // Fecha actual en formato YYYY-MM-DD
    const mensaje = document.getElementById("mensaje");

    if (fechaSeleccionada < hoy) {
        mensaje.textContent = "No podés reservar turnos previos a la fecha actual.";
        mensaje.style.color = "red";
        document.getElementById("horarios").style.display = "none"; // Oculta horarios si la fecha es inválida
    } else {
        mensaje.textContent = "";
        mostrarHorarios(fechaSeleccionada);
    }
}

// Lista de horarios disponibles
const horariosDisponibles = ["09:00", "10:00", "11:00", "15:00", "16:00", "17:00", "18:00", "19:00"];

// Función para mostrar los horarios cuando se selecciona una fecha válida
function mostrarHorarios(fechaSeleccionada) {
    const hoy = new Date().toISOString().split("T")[0]; // Fecha actual
    const ahora = new Date().getHours(); // Hora actual en formato 24h
    const contenedorHorarios = document.getElementById("botones-horarios");
    const seccionHorarios = document.getElementById("horarios");

    // Limpia los horarios anteriores
    contenedorHorarios.innerHTML = "";

    horariosDisponibles.forEach(horario => {
        let boton = document.createElement("button");
        boton.textContent = horario;
        boton.setAttribute("data-horario", horario);

        // Si la fecha es hoy, deshabilitar horarios pasados
        if (fechaSeleccionada === hoy && parseInt(horario.split(":")[0]) <= ahora) {
            boton.disabled = true;
        }

        boton.addEventListener("click", function() {
            seleccionarHorario(fechaSeleccionada, horario);
        });

        contenedorHorarios.appendChild(boton);
    });

    seccionHorarios.style.display = "block";
}

// Función para gestionar la selección de horario
function seleccionarHorario(fecha, hora) {
    const mensajeConfirmacion = `Has seleccionado el turno: ${fecha} a las ${hora}. ¿Quieres confirmar?`;
    if (confirm(mensajeConfirmacion)) {
        alert("Turno reservado correctamente.");
    } else {
        alert("Has cancelado la reserva.");
    }
}
