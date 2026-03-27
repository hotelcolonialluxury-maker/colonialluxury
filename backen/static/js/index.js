// ======================
// ðŸ”¹ TOASTS PROFESIONALES
// ======================
function crearToast(msg, tipo = "success") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "position-fixed top-0 end-0 p-3";
        container.style.zIndex = 1080;
        document.body.appendChild(container);
    }
    const toastEl = document.createElement("div");
    toastEl.className = `toast align-items-center text-bg-${tipo} border-0`;
    toastEl.setAttribute("role", "alert");
    toastEl.setAttribute("aria-live", "assertive");
    toastEl.setAttribute("aria-atomic", "true");
    toastEl.innerHTML = `
        <div class="d-flex">
        <div class="toast-body">${msg}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
    toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}

// ======================
// ðŸ”¹ CARGAR COMENTARIOS
// ======================
async function cargarComentarios() {
    try {
        const res = await fetch(API_COMENTARIOS);
        const data = await res.json();
        const contenedor = document.getElementById('listaComentarios');
        contenedor.innerHTML = '';
        if (!data.length) {
            contenedor.innerHTML = '<p class="text-center text-muted">No hay comentarios aÃºn.</p>';
            return;
        }
        data.forEach(c => {
            const card = `
                <div class="col-md-4">
                    <div class="card shadow-sm p-3 mb-3 animate__animated animate__fadeInUp">
                        <h5 class="card-title">${c.nombre}</h5>
                        <p class="card-text">${c.texto}</p>
                        <div class="text-warning">${'â˜…'.repeat(c.rating || 0)}${'â˜†'.repeat(5 - (c.rating || 0))}
</div>
                        <small class="text-muted">${c.fecha}</small>
                    </div>
                </div>`;
            contenedor.innerHTML += card;
        });
    } catch (error) {
        console.error("Error al cargar comentarios:", error);
        crearToast("Error al cargar comentarios.", "danger");
    }
}

// ======================
// ðŸ”¹ ENVIAR COMENTARIO
// ======================
document.addEventListener('DOMContentLoaded', function() {
    const formComentario = document.getElementById('comentarioForm');
    if (formComentario) {
        formComentario.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const nombre = document.getElementById('nombre').value.trim();
            const email = document.getElementById('email').value.trim();
            const rating = document.getElementById('rating').value;
            const texto = document.getElementById('texto').value.trim();

            if (!nombre || !email || !texto) {
                crearToast('Por favor completa todos los campos', 'warning');
                return;
            }

            try {
                const res = await fetch(API_COMENTARIOS, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        nombre: nombre,
                        email: email,
                        rating: parseInt(rating),
                        texto: texto
                    })
                });

                const data = await res.json();

                if (res.ok) {
                    crearToast('Â¡Gracias por tu comentario! SerÃ¡ revisado antes de publicarse.', 'success');
                    document.getElementById('comentarioForm').reset();
                    cargarComentarios();
                } else {
                    crearToast(data.error || 'No se pudo enviar el comentario', 'danger');
                }
            } catch (error) {
                console.error('Error al enviar comentario:', error);
                crearToast('Error al enviar el comentario. Por favor intenta de nuevo.', 'danger');
            }
        });
    }
});

// ======================
// ðŸ”¹ OBTENER HABITACIÃ“N
// ======================
async function obtenerHabitacionSeleccionada(roomValue) {
    try {
        const res = await fetch(API_HABITACIONES);
        const habitaciones = await res.json();
        console.log("HABITACIONES RAW:", habitaciones);
        console.log("ES ARRAY:", Array.isArray(habitaciones));
        return habitaciones.find(h => h.tipo && h.tipo.toLowerCase() === roomValue.toLowerCase());
    } catch (e) {
        console.error("Error buscando habitaciones:", e);
        crearToast("Error al cargar habitaciones.", "danger");
        return null;
    }
}

// ======================
// ðŸ”¹ CARGAR HABITACIONES 
// ======================
// ======================
async function cargarHabitacionesSelect() {
    const select = document.getElementById("habitacionSelect");
    select.innerHTML = '<option value="">Cargando habitaciones...</option>';

    try {
        const res = await fetch(API_HABITACIONES);
        const data = await res.json();

        if (!data.length) {
            select.innerHTML = '<option value="">No hay habitaciones disponibles</option>';
            return;
        }

        select.innerHTML = '<option value="">Selecciona una habitaciÃ³n</option>';
        data.forEach(h => {
            const option = document.createElement("option");
            option.value = h.id;
            option.textContent = `${h.nombre} - $${h.precio}/noche - Capacidad: ${h.capacidad} personas`;
            select.appendChild(option);
        });

    } catch (error) {
        console.error("Error cargando habitaciones:", error);
        select.innerHTML = '<option value="">Error al cargar habitaciones</option>';
    }
}

// ======================
// ðŸ”¹ CARGAR HABITACIONES EN CARDS (PÃGINA PRINCIPAL)
// ======================
async function cargarHabitacionesCards() {
    const contenedor = document.getElementById("contenedorHabitaciones");
    contenedor.innerHTML = '<div class="text-center w-100"><div class="spinner-border text-warning"></div><p class="mt-2">Cargando habitaciones...</p></div>';

    try {
        // Agregar timestamp para evitar cachÃ©
        const timestamp = new Date().getTime();
        const res = await fetch(`${API_HABITACIONES}?t=${timestamp}`)
        const habitaciones = await res.json();

        console.log("ðŸ“¦ Habitaciones cargadas:", habitaciones.length);

        if (!habitaciones || habitaciones.length === 0) {
            contenedor.innerHTML = '<p class="text-center text-muted w-100">No hay habitaciones disponibles en este momento.</p>';
            return;
        }

        contenedor.innerHTML = '';

        // Imagen por defecto
        const imagenDefault = 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=400&q=80';

        habitaciones.forEach(h => {
            // Construir URL de imagen con timestamp para evitar cachÃ©
            let imagen = imagenDefault;

        if (h.imagen_url) {
                imagen = h.imagen_url.startsWith("http")

                ? h.imagen_url
                : `${h.imagen_url}?v=${Date.now()}`
        }
            
            console.log("IMG FINAL:", imagen);

            
            const card = document.createElement('div');
            card.className = 'card room-card fade-in';
            card.innerHTML = `
                <img src="${imagen}" 
                class="card-img-top" 
                alt="${h.nombre}"
                style="height: 250px; object-fit: cover;">
                <div class="card-body">
                    <h5 class="card-title">${h.nombre}</h5>
                    <p class="card-text">${h.descripcion || 'HabitaciÃ³n cÃ³moda y elegante con todas las comodidades.'}</p>
                    <ul class="features-list list-unstyled mb-3">
                        <li><i class="bi bi-wifi"></i> WiFi gratuito</li>
                        <li><i class="bi bi-tv"></i> Smart TV</li>
                        <li><i class="bi bi-people"></i> Capacidad: ${h.capacidad} personas</li>
                        <li><i class="bi bi-door-closed"></i> Tipo: ${h.tipo.charAt(0).toUpperCase() + h.tipo.slice(1)}</li>
                    </ul>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="price">$${h.precio}/noche</span>
                        <button class="btn btn-gold" onclick="abrirModalReserva(${h.id})">
                            <i class="bi bi-calendar-plus"></i> Reservar
                        </button>
                    </div>
                </div>
            `;
            contenedor.appendChild(card);
        });

        console.log("âœ… Habitaciones renderizadas correctamente");

    } catch (error) {
        console.error("âŒ Error al cargar habitaciones:", error);
        contenedor.innerHTML = '<p class="text-center text-danger w-100">Error al cargar las habitaciones. Por favor, intenta de nuevo.</p>';
    }
}

// ======================
// ðŸ”¹ ABRIR MODAL DE RESERVA CON HABITACIÃ“N PRESELECCIONADA
// ======================
function abrirModalReserva(habitacionId) {
    const modal = new bootstrap.Modal(document.getElementById('reservationModal'));
    modal.show();
    
    // Preseleccionar la habitaciÃ³n en el select
    setTimeout(() => {
        const select = document.getElementById('habitacionSelect');
        if (select && habitacionId) {
            select.value = habitacionId;
        }
    }, 100);
}




// ======================
// ðŸ”¹ ENVIAR RESERVA
// ======================
function calcularDiasReserva(fechaEntrada, fechaSalida) {
    const entrada = new Date(fechaEntrada);
    const salida = new Date(fechaSalida);

    if (Number.isNaN(entrada.getTime()) || Number.isNaN(salida.getTime())) {
        return 0;
    }

    const diffMs = salida - entrada;
    const dias = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    return dias > 0 ? dias : 0;
}

async function calcularMontoEstimadoReserva(payload) {
    try {
        const res = await fetch(API_HABITACIONES);
        if (!res.ok) return 0;

        const habitaciones = await res.json();
        const habitacion = habitaciones.find(h => Number(h.id) === Number(payload.habitacion_id));
        if (!habitacion) return 0;

        const dias = calcularDiasReserva(payload.fecha_entrada, payload.fecha_salida);
        return dias > 0 ? Number(habitacion.precio || 0) * dias : 0;
    } catch (error) {
        console.warn("No se pudo calcular el monto estimado de la reserva", error);
        return 0;
    }
}

document.getElementById("formReserva")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    const payload = {
        habitacion_id: parseInt(formData.get("habitacion_id")),
        num_personas: parseInt(formData.get("huespedes").split(" ")[0]) || 1,
        fecha_entrada: formData.get("fecha_entrada"),
        fecha_salida: formData.get("fecha_salida"),
        notas: formData.get("notas"),
        nombre: formData.get("nombre"),
        email: formData.get("correo"),
        telefono: formData.get("telefono"),
        identificacion: formData.get("identificacion")
    };

    // ValidaciÃ³n bÃ¡sica
    if (!payload.habitacion_id || !payload.fecha_entrada || !payload.fecha_salida) {
        crearToast("Completa todos los campos obligatorios", "warning");
        return;
    }

    try {
        const res = await fetch("/api/reservas/publica", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const json = await res.json();

        if (res.ok) {
            const montoEstimado = await calcularMontoEstimadoReserva(payload);
            localStorage.setItem("reserva_id", String(json.reserva_id || ""));
            if (montoEstimado > 0) {
                localStorage.setItem("monto_total", String(montoEstimado));
            }
            crearToast("Reserva creada correctamente. Nos comunicaremos contigo ðŸ“ž", "success");
            this.reset();
            bootstrap.Modal.getInstance(
                document.getElementById("reservationModal")
            ).hide();
        } else {
            crearToast(json.error || "Error al crear la reserva", "danger");
        }

    } catch (error) {
        console.error("Error creando reserva:", error);
        crearToast("Error de conexiÃ³n con el servidor.", "danger");
    }
});

// ============================
// ðŸ” LOGIN DEL CLIENTE (INDEX)
// ============================
document.getElementById("formLogin")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = e.target.email.value.trim();
    const password = e.target.password.value.trim();

    if (!email || !password) {
        crearToast("Todos los campos son obligatorios", "warning");
        return;
    }

    try {
        const res = await fetch(API_LOGIN, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            crearToast(data.error || "Correo o contraseÃ±a incorrectos", "danger");
            return;
        }

        // Guardamos token Ãºnico
        localStorage.setItem("token", data.token);
        localStorage.setItem("usuario", JSON.stringify(data.usuario));

        // Diferenciamos rol
        if (data.usuario.rol === "admin") {
            crearToast("Bienvenido administrador âœ”ï¸", "success");
        } else {
            crearToast("Bienvenido cliente âœ”ï¸", "success");
        }

        // Cerramos modal
        const modal = bootstrap.Modal.getInstance(document.getElementById("loginModal"));
        modal?.hide();

        e.target.reset();

    } catch (err) {
        console.error("Error login:", err);
        crearToast("Error de conexiÃ³n con el servidor", "danger");
    }
});

// =====================
// ðŸ”¹ FUNCIONES RESERVAS (ADMIN)
// =====================
async function cargarReservas() {
    const token = localStorage.getItem('token');
    if (!token) {
        crearToast("Debes iniciar sesiÃ³n como admin", "warning");
        window.location.href = "login";
        return;
    }

    try {
        const res = await fetch(API_RESERVAS, {
            headers: { 'Authorization': 'Bearer ' + token }
        });

        if (!res.ok) {
            console.log("Error cargando reservas:", res.status, await res.text());
            crearToast("Error cargando reservas", "danger");
            return;
        }

        const reservas = await res.json();
        const tabla = document.getElementById("tablaReservas");

        tabla.innerHTML = reservas.map(r => `
            <tr>
                <td>${r.id}</td>
                <td>${r.usuario?.nombre || "Sin nombre"}</td>
                <td>${r.habitacion?.nombre || "No encontrada"}</td>
                <td>${r.fecha_entrada}</td>
                <td>${r.fecha_salida}</td>
                <td>${r.num_personas}</td>
                <td>$${r.precio_total}</td>
                <td>
                    <select class="form-select form-select-sm" onchange="cambiarEstado(${r.id}, this.value)">
                        <option value="pendiente" ${r.estado === "pendiente" ? "selected" : ""}>Pendiente</option>
                        <option value="confirmada" ${r.estado === "confirmada" ? "selected" : ""}>Confirmada</option>
                        <option value="cancelada" ${r.estado === "cancelada" ? "selected" : ""}>Cancelada</option>
                    </select>
                </td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="eliminarReserva(${r.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join("");

    } catch (err) {
        console.error(err);
        crearToast("Error de conexiÃ³n con el servidor", "danger");
    }
}

async function cambiarEstado(id, estado) {
    const token = localStorage.getItem('token');
    if (!token) { crearToast("Debes iniciar sesiÃ³n", "warning"); return; }

    try {
        const res = await fetch(`${API_RESERVAS}/${id}/estado`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
            body: JSON.stringify({ estado })
        });

        if (res.ok) crearToast("Estado actualizado âœ”ï¸", "success");
        else crearToast("No se pudo actualizar el estado âŒ", "danger");

    } catch (err) {
        console.error(err);
        crearToast("Error de conexiÃ³n", "danger");
    }
}

async function eliminarReserva(id) {
    const token = localStorage.getItem('token');
    if (!token) { crearToast("Debes iniciar sesiÃ³n", "warning"); return; }

    if (!confirm("Â¿Eliminar esta reserva?")) return;

    try {
        const res = await fetch(`${API_RESERVAS}/${id}`, {

            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });

        if (res.ok) {
            crearToast("Reserva eliminada âœ”ï¸", "success");
            cargarReservas();
        } else crearToast("No se pudo eliminar la reserva âŒ", "danger");

    } catch (err) {
        console.error(err);
        crearToast("Error de conexiÃ³n", "danger");
    }
}
// Enviar mensaje desde el index
document.getElementById('formContacto')?.addEventListener('submit', async function(e){
    e.preventDefault();

    const nombre = document.getElementById('nombreIndex').value.trim();
    const email = document.getElementById('emailIndex').value.trim();
    const telefono = document.getElementById('telefonoIndex').value.trim();
    const asunto = document.getElementById('asuntoIndex').value.trim();
    const mensaje = document.getElementById('mensajeIndex').value.trim();

    if(!nombre || !email || !mensaje) {
        alert('Completa todos los campos obligatorios');
        return;
    }

    try {
        const res = await fetch(API_CONTACTOS, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, email, telefono, asunto, mensaje })
        });

        if(res.ok){
            alert('Mensaje enviado âœ”ï¸');
            this.reset();
        } else {
            const data = await res.json();
            alert(data.error || 'Error al enviar mensaje');
        }

    } catch(err){
        console.error(err);
        alert('Error de conexiÃ³n con el servidor');
    }
});




// ======================
// ðŸ”¹ INICIALIZAR
// ======================
document.addEventListener('DOMContentLoaded', function() {
    cargarComentarios();
    cargarHabitacionesCards(); // Cargar habitaciones en la pÃ¡gina
    cargarHabitacionesSelect(); // Cargar habitaciones en el modal
});

fetch(API_PORTADA)

.then(res => res.json())
.then(data => {
    console.log("PORTADA INDEX:", data);
    if (data.imagen) {
        document.querySelector(".hero").style.backgroundImage =
            `url(${data.imagen}?v=${Date.now()})`;
    }
})
.catch(err => console.error("Error cargando portada", err));



// ================================
// CREAR PAGO (USUARIO)
// ================================
let metodoSeleccionado = null;

// ================================
// SELECCIONAR MÃ‰TODO DE PAGO
// ================================
document.querySelectorAll(".metodo-pago").forEach(card => {
    card.addEventListener("click", () => {

        // quitar selecciÃ³n previa
        document.querySelectorAll(".metodo-pago").forEach(c => {
            c.classList.remove("border", "border-primary");
        });

        // marcar seleccionada
        card.classList.add("border", "border-primary");

        metodoSeleccionado = card.dataset.metodo;

        // habilitar botÃ³n pagar
        document.getElementById("btnPagar").disabled = false;
    });
});

document.getElementById("btnPagar")?.addEventListener("click", async () => {

    if (!metodoSeleccionado) {
        crearToast("Selecciona un metodo de pago", "warning");
        return;
    }

    const reservaId = Number(localStorage.getItem("reserva_id") || window.RESERVA_ID || 0);
    const montoTotal = Number(localStorage.getItem("monto_total") || window.MONTO_TOTAL || 0);

    if (!reservaId || !montoTotal) {
        crearToast("Primero crea una reserva para generar el pago", "warning");
        return;
    }

    try {
        const res = await fetch(API_PAGOS, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                reserva_id: reservaId,
                monto: montoTotal,
                metodo: metodoSeleccionado
            })
        });

        const data = await res.json();

        if (!res.ok) {
            crearToast(data.message || "Error al procesar el pago", "danger");
            return;
        }

        // ðŸ’³ TARJETA â†’ REDIRECCIÃ“N
        if (data.tipo === "tarjeta") {
            window.location.href = data.url_pago;
            return;
        }

        // ðŸ¦ TRANSFERENCIA
        mostrarDatosTransferencia(data.pago_id);

    } catch (error) {
        console.error(error);
        crearToast("Error de conexiÃ³n", "danger");
    }
});

// ================================
// DATOS TRANSFERENCIA
// ================================
function mostrarDatosTransferencia(pagoId) {
    const contenedor = document.getElementById("datosTransferencia");

    contenedor.innerHTML = `
        <div class="alert alert-info">
            <h5>Transferencia bancaria</h5>
            <p><strong>Banco:</strong> Bancolombia</p>
            <p><strong>Cuenta:</strong> 123456789</p>
            <p><strong>Tipo:</strong> Ahorros</p>
            <p><strong>Referencia:</strong> PAGO-${pagoId}</p>
            <p class="mt-2 text-warning">
                Tu reserva se confirmarÃ¡ cuando el administrador valide el pago.
            </p>
        </div>
    `;
}

