 // ✅ Validar token y rol de admin al cargar la página
const token = localStorage.getItem('token'); // ⬅️ Cambiar de 'token_admin' a 'token'
if (token) {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (payload.rol !== 'admin') {
        alert('No tienes permisos para acceder');
        window.location.href = 'login';
    }
} else {
    window.location.href = 'login';
}

if (localStorage.getItem("token")) {
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function () {
        window.history.pushState(null, "", window.location.href);
    };
}
document.addEventListener("DOMContentLoaded", function () {

    // ==============================
    // BOTÓN CERRAR SESIÓN
    // ==============================
    const btn = document.getElementById("btnCerrarSesion");

    if (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            localStorage.clear();
            window.location.replace("login");
        });
    } else {
        console.warn("Botón cerrar sesión no encontrado");
    }

    // ==============================
    // CIERRE POR INACTIVIDAD
    // ==============================
    const TIEMPO_INACTIVIDAD = 10 * 60 * 1000; // 10 minutos
    let temporizador;

    function cerrarSesionInactividad() {
        console.warn("Sesión cerrada por inactividad");
        localStorage.clear();
        window.location.replace("login");
    }

    function reiniciarTemporizador() {
        clearTimeout(temporizador);
        temporizador = setTimeout(cerrarSesionInactividad, TIEMPO_INACTIVIDAD);
    }

    ["mousemove", "mousedown", "keypress", "scroll", "touchstart"].forEach(evento => {
        document.addEventListener(evento, reiniciarTemporizador, true);
    });

    reiniciarTemporizador();
});

// ======================
// 🔹 DASHBOARD DATA
// ======================
// ======================
async function cargarDashboard() {
    try {
        const token = localStorage.getItem('token');
        
        console.log("🔄 Cargando dashboard...");
        
        // Cargar todos los datos en paralelo
        const [habRes, resRes, pagosRes, contactosRes, comentariosRes] = await Promise.all([
            fetch(API_HABITACIONES),
            fetch(API_RESERVAS, { 
                headers: { 'Authorization': 'Bearer ' + token }
            }),
            fetch(API_ADMIN_PAGOS, {
                headers: { 'Authorization': 'Bearer ' + token }
            }),
            fetch(API_ADMIN_CONTACTOS, {
                headers: { 'Authorization': 'Bearer ' + token }
            }),
            fetch(API_ADMIN_COMENTARIOS, {
                headers: { 'Authorization': 'Bearer ' + token }
            })
        ]);

        // Verificar si las peticiones fueron exitosas
        if (!habRes.ok) {
            console.error('❌ Error cargando habitaciones:', habRes.status);
        }
        if (!resRes.ok) {
            console.error('❌ Error cargando reservas:', resRes.status);
        }
        if (!pagosRes.ok) {
            console.error('❌ Error cargando pagos:', pagosRes.status);
        }
        if (!contactosRes.ok) {
            console.error('❌ Error cargando contactos:', contactosRes.status);
        }
        if (!comentariosRes.ok) {
            console.error('❌ Error cargando comentarios:', comentariosRes.status);
        }

        const habitaciones = await habRes.json();
        const reservas = await resRes.json();
        const pagos = await pagosRes.json();
        const contactos = await contactosRes.json();
        const comentarios = await comentariosRes.json();

        console.log("📊 Datos cargados:", {
            habitaciones: habitaciones.length,
            reservas: reservas.length,
            pagos: pagos.length,
            contactos: contactos.length,
            comentarios: comentarios.length
        });
         // =================== ESTADÍSTICAS PRINCIPALES ===================
        
        // Total Habitaciones
        const totalHabitaciones = habitaciones.length || 0;
        document.getElementById("dashHabitaciones").innerText = totalHabitaciones;
        console.log("✅ Total habitaciones:", totalHabitaciones);

        // Total Reservas
        const totalReservas = reservas.length || 0;
        document.getElementById("dashReservas").innerText = totalReservas;
        console.log("✅ Total reservas:", totalReservas);

        // Total de Pagos
        const totalPagos = pagos.reduce((sum, p) => sum + (Number(p.monto) || 0), 0);
        document.getElementById("dashPagos").innerText = "$" + totalPagos.toLocaleString('es-CO');
        console.log("✅ Total pagos:", totalPagos);

        // Total Mensajes de Contacto
        const totalContactos = contactos.length || 0;
        document.getElementById("dashContactos").innerText = totalContactos;
        console.log("✅ Total contactos:", totalContactos);

        // =================== ESTADÍSTICAS DE COMENTARIOS ===================
        
        const comentariosPendientes = comentarios.filter(c => c.estado === "pendiente").length;
        const comentariosAprobados = comentarios.filter(c => c.estado === "aprobado").length;
        const totalComentarios = comentarios.length || 0;

        document.getElementById("dashComentariosPendientes").innerText = comentariosPendientes;
        document.getElementById("dashComentariosAprobados").innerText = comentariosAprobados;
        document.getElementById("dashComentariosTotal").innerText = totalComentarios;

        console.log("✅ Comentarios:", {
            pendientes: comentariosPendientes,
            aprobados: comentariosAprobados,
            total: totalComentarios
        });

        // =================== ESTADÍSTICAS DE RESERVAS ===================
        
        const reservasConfirmadas = reservas.filter(r => r.estado === "confirmada").length;
        const reservasPendientes = reservas.filter(r => r.estado === "pendiente").length;
        const reservasCanceladas = reservas.filter(r => r.estado === "cancelada").length;

        document.getElementById("dashReservasConfirmadas").innerText = reservasConfirmadas;
        document.getElementById("dashReservasPendientes").innerText = reservasPendientes;
        document.getElementById("dashReservasCanceladas").innerText = reservasCanceladas;

        console.log("✅ Reservas por estado:", {
            confirmadas: reservasConfirmadas,
            pendientes: reservasPendientes,
            canceladas: reservasCanceladas
        });

        // =================== ÚLTIMAS 5 RESERVAS ===================
        const tabla = document.getElementById("tablaReservasDashboard");
        
        if (!reservas || reservas.length === 0) {
            tabla.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">No hay reservas registradas aún</td></tr>';
        } else {
            const ultimasReservas = reservas.slice(-5).reverse();
            
            tabla.innerHTML = ultimasReservas.map(r => {
                let badgeColor = 'warning';
                if (r.estado === 'confirmada') badgeColor = 'success';
                else if (r.estado === 'cancelada') badgeColor = 'danger';
                
                return `
                    <tr>
                        <td class="ps-3"><strong>#${r.id}</strong></td>
                        <td>${r.nombre || (r.usuario ? r.usuario.nombre : "N/A")}</td>
                        <td>${r.habitacion ? r.habitacion.nombre : "N/A"}</td>
                        <td><small>${r.fecha_entrada || "N/A"}</small></td>
                        <td><small>${r.fecha_salida || "N/A"}</small></td>
                        <td><strong class="text-success">$${r.precio_total || 0}</strong></td>
                        <td>
                            <span class="badge bg-${badgeColor}">
                                ${r.estado}
                            </span>
                        </td>
                    </tr>
                `;
            }).join("");
        }

        console.log("✅ Dashboard cargado correctamente");

    } catch (err) {
        console.error("❌ Error crítico cargando dashboard:", err);
        crearToast("Error de conexión al cargar dashboard", "danger");
        
        // Mostrar valores por defecto en caso de error
        document.getElementById("dashHabitaciones").innerText = "0";
        document.getElementById("dashReservas").innerText = "0";
        document.getElementById("dashPagos").innerText = "$0";
        document.getElementById("dashContactos").innerText = "0";
        document.getElementById("dashComentariosPendientes").innerText = "0";
        document.getElementById("dashComentariosAprobados").innerText = "0";
        document.getElementById("dashComentariosTotal").innerText = "0";
        document.getElementById("dashReservasConfirmadas").innerText = "0";
        document.getElementById("dashReservasPendientes").innerText = "0";
        document.getElementById("dashReservasCanceladas").innerText = "0";
        document.getElementById("tablaReservasDashboard").innerHTML = 
            '<tr><td colspan="7" class="text-center text-danger py-3">⚠️ Error al cargar datos del dashboard</td></tr>';
    }
}

// ======================
// 🔹 INICIALIZACIÓN
// ======================
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Iniciando panel de administración...");
    
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.warn("⚠️ No hay token, redirigiendo a login");
        window.location.href = 'login';
        return;
    }
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        console.log("👤 Usuario autenticado:", payload);
        
        if (payload.rol !== 'admin') {
            alert('⛔ No tienes permisos para acceder al panel de administración');
            localStorage.clear();
            window.location.href = 'login';
            return;
        }
        
        console.log("✅ Acceso autorizado - Rol: admin");
        
    } catch (e) {
        console.error('❌ Token inválido:', e);
        localStorage.clear();
        window.location.href = 'login';
        return;
    }
    
    // Cargar dashboard inicial
    console.log("📊 Cargando dashboard inicial...");
    mostrarSeccion('dashboard');
});

// ======================
// 🔹 TOASTS PROFESIONALES
// ======================
function crearToast(msg, tipo = "success", duracion = 4000, icono = "") {
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
            ${icono ? `<i class="bi ${icono} me-2"></i>` : ""}
            <div class="toast-body">${msg}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: duracion });
    toast.show();

    toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}


// ======================
// 🔹 MOSTRAR SECCIONES
// ======================
function mostrarSeccion(id) {
    console.log("📍 Mostrando sección:", id);

    document.querySelectorAll('.seccion').forEach(s => s.style.display = 'none');
    
    const seccion = document.getElementById(id);
    if (!seccion) return;

    seccion.style.display = 'block';

    switch (id) {
        case 'dashboard':
            cargarDashboard();
            break;
        case 'habitaciones':
            cargarHabitaciones();
            break;
        case 'reservas':
            cargarReservas();
            break;
        case 'comentarios':
            cargarComentarios();
            break;
        case 'pagos':
            cargarPagos();
            break;
        case 'contactos':
            cargarContactos();
            break;
    }
}

// ======================
// 🔹 VISTA PREVIA DE IMAGEN
// ======================
document.getElementById('imagenHabitacion')?.addEventListener('change', function (e) {
    const file = e.target.files[0];
    const preview = document.getElementById('vistaPrevia');
    const img = document.getElementById('imagenPreview');

    if (!file) {
        preview.style.display = 'none';
        return;
    }

    if (!file.type.startsWith("image/")) {
        crearToast("El archivo no es una imagen válida", "warning");
        e.target.value = "";
        preview.style.display = 'none';
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        img.src = reader.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
});

// ======================
// 🔹 CARGAR HABITACIONES
// ======================
async function cargarHabitaciones() {
    try {
        console.log("🔄 Cargando habitaciones...");
        
        const timestamp = new Date().getTime();
        const tabla = document.getElementById('tablaHabitaciones');
        const imagenDefault = `${window.location.origin}/static/img/default-room.jpg`;

        // Mostrar URL en consola para depuración
        console.log("📡 Fetch URL:", `${API_HABITACIONES}?t=${timestamp}`);

        const res = await fetch(`${API_HABITACIONES}?t=${timestamp}`);

        if (!res.ok) {
            console.error('❌ Error cargando habitaciones:', res.status);
            crearToast('Error al cargar habitaciones', 'danger');
            tabla.innerHTML = '<tr><td colspan="8" class="text-center text-danger">No se pudieron cargar las habitaciones</td></tr>';
            return;
        }

        const data = await res.json();
        const habitaciones = Array.isArray(data) ? data : data.habitaciones || [];

        console.log("📦 Habitaciones recibidas:", habitaciones.length);

        if (habitaciones.length === 0) {
            tabla.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No hay habitaciones registradas</td></tr>';
            return;
        }

        tabla.innerHTML = habitaciones.map(h => {
            const descripcionSegura = (h.descripcion || '').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, ' ');
            const nombreSeguro = (h.nombre || '').replace(/'/g, "\\'");
            const imagenMostrar = h.imagen
                ? `${window.location.origin}/static/uploads/habitaciones/${h.imagen}?t=${timestamp}`
                : imagenDefault;

            return `
                <tr>
                    <td>${h.id}</td>
                    <td>
                        <img src="${imagenMostrar}"  
                            alt="${h.nombre || ''}" 
                            style="width: 80px; height: 60px; object-fit: cover; border-radius: 5px;"
                            onerror="this.onerror=null; this.src='${imagenDefault}'">
                    </td>
                    <td>${h.nombre || '-'}</td>
                    <td>$${h.precio || 0}</td>
                    <td>${h.capacidad || 0} personas</td>
                    <td><span class="badge bg-info">${h.tipo || '-'}</span></td>
                    <td>${h.descripcion || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-warning me-1" 
                            onclick="editarHabitacion(${h.id}, '${nombreSeguro}', ${h.precio || 0}, ${h.capacidad || 0}, '${h.tipo || ''}', '${descripcionSegura}', '${h.imagen || ''}')">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarHabitacion(${h.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        console.log("✅ Habitaciones cargadas correctamente");

    } catch (error) {
        console.error('❌ Error completo:', error);
        crearToast('Error de conexión al cargar habitaciones', 'danger', 4000, 'bi-exclamation-triangle');
    }
}

// ======================
// 🔹 AGREGAR HABITACIÓN
// ======================
async function agregarHabitacion() {
    const nombre = document.getElementById('nombreHabitacion').value.trim();
    const precio = document.getElementById('precioHabitacion').value;
    const capacidad = document.getElementById('capacidadHabitacion').value;
    const tipo = document.getElementById('tipoHabitacion').value;
    const descripcion = document.getElementById('descripcionHabitacion').value;
    const imagen = document.getElementById('imagenHabitacion').files[0];

    if (!nombre || !precio || !capacidad || !tipo) {
        crearToast("Completa los campos obligatorios", "warning");
        return;
    }

    const token = localStorage.getItem("token");

    const formData = new FormData();
    formData.append("nombre", nombre);
    formData.append("precio", precio);
    formData.append("capacidad", capacidad);
    formData.append("tipo", tipo);
    formData.append("descripcion", descripcion);

    if (imagen) {
        formData.append("imagen", imagen);
    }

    try {
        const res = await fetch(API_ADMIN_HABITACIONES, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            },
            body: formData
        });

        const data = await res.json();

        if (!res.ok) {
            crearToast(data.error || "Error al crear habitación", "danger");
            return;
        }

        crearToast("Habitación creada ✔️", "success");

        document.querySelector(".formulario-habitacion").querySelectorAll("input, textarea, select").forEach(e => e.value = "");
        document.getElementById("vistaPrevia").style.display = "none";

        cargarHabitaciones();

    } catch (err) {
        console.error(err);
        crearToast("Error de conexión", "danger");
    }
}
// ======================
// 🔹 EDITAR HABITACIÓN
// ======================
function editarHabitacion(id, nombre, precio, capacidad, tipo, descripcion, imagen) {
    console.log("✏️ Editando habitación ID:", id);
    console.log("📸 Imagen actual:", imagen);
    
    // Llenar el formulario con los datos actuales
    document.getElementById('nombreHabitacion').value = nombre;
    document.getElementById('precioHabitacion').value = precio;
    document.getElementById('capacidadHabitacion').value = capacidad;
    document.getElementById('tipoHabitacion').value = tipo;
    document.getElementById('descripcionHabitacion').value = descripcion;
    
    // Limpiar el input de archivo (importante)
    document.getElementById('imagenHabitacion').value = '';
    
    // Mostrar vista previa de la imagen actual
    if (imagen) {
        const preview = document.getElementById('vistaPrevia');
        const img = document.getElementById('imagenPreview');
        
        // Construir URL correcta y agregar timestamp para evitar caché
        const timestamp = new Date().getTime();
        const imagenUrl = imagen.startsWith("http") 
            ? `${imagen}?t=${timestamp}`
            : `${window.location.origin}/static/uploads/habitaciones/${imagen}?t=${timestamp}`;
        
        img.src = imagenUrl;
        preview.style.display = 'block';
        
        console.log("🖼️ Vista previa cargada:", imagenUrl);
    }

    // Cambiar el botón a modo "Guardar"
    const btn = document.querySelector("#habitaciones button.btn-accion");
    btn.innerHTML = '<i class="bi bi-save"></i> Guardar cambios';
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-success');

    // Función para guardar cambios
    btn.onclick = async () => {
        console.log("💾 Guardando cambios de habitación ID:", id);
        
        const token = localStorage.getItem('token');
        const fileInput = document.getElementById('imagenHabitacion');
        const formData = new FormData();

        // Agregar todos los campos
        formData.append("nombre", document.getElementById('nombreHabitacion').value);
        formData.append("precio", document.getElementById('precioHabitacion').value);
        formData.append("capacidad", document.getElementById('capacidadHabitacion').value);
        formData.append("tipo", document.getElementById('tipoHabitacion').value);
        formData.append("descripcion", document.getElementById('descripcionHabitacion').value);
        
        // Verificar si se seleccionó una nueva imagen
        if (fileInput.files.length > 0) {
            formData.append("imagen", fileInput.files[0]);
            console.log("📤 Nueva imagen seleccionada:", fileInput.files[0].name);
        } else {
            console.log("ℹ️ No se seleccionó nueva imagen, se mantendrá la actual");
        }

        try {
            console.log("🔄 Enviando petición PUT...");
            
            const res = await fetch(`${API_HABITACIONES}/${id}`, {
                method: "PUT",
                headers: {
                    "Authorization": "Bearer " + token
                },
                body: formData
            });

            const data = await res.json();
            
            console.log("📡 Respuesta del servidor:", data);

            if (!res.ok) {
                console.error("❌ Error del servidor:", data.error);
                crearToast(data.error || "Error al actualizar", "danger");
                return;
            }

            console.log("✅ Habitación actualizada correctamente");
            crearToast("Habitación actualizada correctamente ✔️", "success");

            // Restaurar botón a modo "Agregar"
            btn.innerHTML = '<i class="bi bi-plus-circle"></i> Agregar Habitación';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-primary');
            btn.onclick = agregarHabitacion;
            
            // Limpiar formulario
            document.getElementById('nombreHabitacion').value = '';
            document.getElementById('precioHabitacion').value = '';
            document.getElementById('capacidadHabitacion').value = '';
            document.getElementById('tipoHabitacion').value = '';
            document.getElementById('descripcionHabitacion').value = '';
            document.getElementById('imagenHabitacion').value = '';
            document.getElementById('vistaPrevia').style.display = 'none';
            
            // ⚠️ IMPORTANTE: Esperar un momento antes de recargar
            setTimeout(() => {
                console.log("🔄 Recargando lista de habitaciones...");
                cargarHabitaciones();
            }, 500);

        } catch (err) {
            console.error("❌ Error de conexión:", err);
            crearToast("Error de conexión al actualizar", "danger");
        }
    };
}

// =================== ELIMINAR HABITACIÓN ===================
async function eliminarHabitacion(id) {
    if (!confirm("¿Seguro que deseas eliminar esta habitación?")) return;

    const token = localStorage.getItem('token');

    try {
        const res = await fetch(`${API_HABITACIONES}/${id}`, {

            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });

        if (res.ok) {
            crearToast("Habitación eliminada ✔️", "success");
            cargarHabitaciones();
        } else {
            const data = await res.json();
            crearToast(data.error || "No se pudo eliminar", "danger");
        }
    } catch (err) {
        console.error(err);
        crearToast("Error de conexión", "danger");
    }
}
// =====================
// 🔹 CARGAR RESERVAS
// =====================
async function cargarReservas() {
    const token = localStorage.getItem('token');

    if (!token) {
        crearToast("Debes iniciar sesión como admin", "warning");
        window.location.href = "login";
        return;
    }

    try {
        const res = await fetch(`${API_RESERVAS}`, {

            method: 'GET',
            headers: { 
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error("Error cargando reservas:", res.status, errorText);
            
            if (res.status === 401) {
                crearToast("Sesión expirada. Inicia sesión nuevamente", "danger");
                localStorage.clear();
                window.location.href = "login";
                return;
            }
            
            crearToast("Error cargando reservas", "danger");
            return;
        }

        const reservas = await res.json();
        const tabla = document.getElementById("tablaReservas");

        if (!reservas || reservas.length === 0) {
            tabla.innerHTML = '<tr><td colspan="9" class="text-center">No hay reservas registradas</td></tr>';
            return;
        }

        tabla.innerHTML = reservas.map(r => `
            <tr>
                <td>${r.id}</td>
                <td>${r.nombre || r.usuario?.nombre || "Sin nombre"}</td>
                <td>${r.habitacion?.nombre || "No encontrada"}</td>
                <td>${r.fecha_entrada}</td>
                <td>${r.fecha_salida}</td>
                <td>${r.num_personas}</td>
                <td>$${r.precio_total}</td>
                <td>
                    <select class="form-select form-select-sm" onchange="cambiarEstadoReserva(${r.id}, this.value)">
                        <option value="pendiente" ${r.estado === "pendiente" ? "selected" : ""}>Pendiente</option>
                        <option value="confirmada" ${r.estado === "confirmada" ? "selected" : ""}>Confirmada</option>
                        <option value="cancelada" ${r.estado === "cancelada" ? "selected" : ""}>Cancelada</option>
                    </select>
                </td>
                <td>
                    <button class="btn btn-sm btn-info me-1" onclick="verReserva(${r.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="eliminarReserva(${r.id})">
                        <i class="bi bi-trash"></i>
                    </button>    
                </td>
            </tr>
        `).join("");

    } catch (err) {
        console.error("Error cargando reservas:", err);
        crearToast("Error de conexión con el servidor", "danger");
    }
}
async function cambiarEstadoReserva(id, estado) {
    const token = localStorage.getItem('token');
    if (!token) {
        crearToast("Debes iniciar sesión como admin", "warning");
        return;
    }

    try {
        const res = await fetch(`${API_ADMIN_RESERVAS}/${id}/estado`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ estado })
        });

        if (res.ok) {
            crearToast("Estado actualizado ✔️", "success");
            await cargarReservas(); // refrescar tabla
            await cargarDashboard();
        } else {
            const err = await res.text();
            console.log("Error cambiar estado:", err);
            crearToast("No se pudo actualizar el estado ❌", "danger");
        }
    } catch (err) {
        console.error(err);
        crearToast("Error de conexión", "danger");
    }
}

async function eliminarReserva(id) {
    const token = localStorage.getItem("token");

    if (!token) {
        crearToast("Debes iniciar sesión como admin", "warning");
        return;
    }

    if (!confirm("¿Eliminar esta reserva?")) return;

    try {
        const res = await fetch(`${API_RESERVAS}/${id}`, {
            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });

        if (res.ok) {
            crearToast("Reserva eliminada ✔️", "success");
            cargarReservas();
        } else {
            const err = await res.text();
            console.log("Error eliminar reserva:", err);
            crearToast("No se pudo eliminar la reserva ❌", "danger");
        }
    } catch (err) {
        console.error(err);
        crearToast("Error de conexión con el servidor", "danger");
    }
}

// =================== PAGOS ===================
function agregarPago() {
    crearToast("Los pagos se crean desde una reserva activa en el index.", "warning");
}

async function cargarPagos() {
    try {
        const res = await fetch(`${API_ADMIN_PAGOS}`, {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token")
            }
        });

        if (!res.ok) {
            crearToast('Error al cargar pagos', 'danger');
            return;
        }

        const pagos = await res.json();
        const tabla = document.getElementById("tablaPagos");

        if (!pagos || pagos.length === 0) {
            tabla.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        No hay pagos registrados
                    </td>
                </tr>`;
            return;
        }

        tabla.innerHTML = pagos.map(p => {
            let badge = "warning";
            if (p.estado === "pagado") badge = "success";
            if (p.estado === "rechazado") badge = "danger";

            let acciones = "-";

            // 👉 SOLO transferencias pendientes
            if (p.metodo === "transferencia" && p.estado === "pendiente") {
                acciones = `
                    <button class="btn btn-sm btn-success me-1" onclick="confirmarPago(${p.id})">
                        Confirmar
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="rechazarPago(${p.id})">
                        Rechazar
                    </button>
                `;
            }

            return `
                <tr>
                    <td>${p.cliente}</td>
                    <td>$${p.monto.toLocaleString()}</td>
                    <td>${p.metodo}</td>
                    <td>
                        <span class="badge bg-${badge}">
                            ${p.estado}
                        </span>
                    </td>
                    <td>${p.fecha || "-"}</td>
                    <td>${acciones}</td>
                </tr>
            `;
        }).join("");

    } catch (error) {
        console.error(error);
        crearToast('Error de conexión', 'danger');
    }
}

async function confirmarPago(id) {
    if (!confirm("¿Confirmar este pago por transferencia?")) return;

    const res = await fetch(`${API_ADMIN_PAGOS}/${id}/confirmar`, {
        method: "PUT",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    });

    if (res.ok) {
        crearToast("Pago confirmado", "success");
        cargarPagos();
    } else {
        crearToast("No se pudo confirmar el pago", "danger");
    }
}

async function rechazarPago(id) {
    if (!confirm("¿Rechazar este pago?")) return;

    const res = await fetch(`${API_ADMIN_PAGOS}/${id}/rechazar`, {
        method: "PUT",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    });

    if (res.ok) {
        crearToast("Pago rechazado", "warning");
        cargarPagos();
    } else {
        crearToast("No se pudo rechazar el pago", "danger");
    }
}
// =================== COMENTARIOS ===================
async function cargarComentarios(){
    try {
        const res = await fetch(API_ADMIN_COMENTARIOS, {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token")
            }
        });

        if (!res.ok) {
            console.error("Error cargando comentarios:", res.status);
            return;
        }

        const comentarios = await res.json();
        const tbody = document.querySelector("#tablaComentarios tbody");
        tbody.innerHTML = "";

        comentarios.forEach(c => {
            let colorEstado =
                c.estado === "aprobado" ? "success" :
                c.estado === "rechazado" ? "danger" : "warning";

            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${c.id}</td>
                <td>${c.nombre}</td>
                <td>${c.email}</td>
                <td>${c.rating ?? "-"}</td>
                <td>${c.texto}</td>
                <td>${c.fecha}</td>
                <td><span class="badge bg-${colorEstado}">${c.estado}</span></td>
                <td>
                    <button class="btn btn-sm btn-success me-1" onclick="cambiarEstado(${c.id}, 'aprobar')">Aprobar</button>
                    <button class="btn btn-sm btn-warning me-1" onclick="cambiarEstado(${c.id}, 'rechazar')">Rechazar</button>
                    <button class="btn btn-sm btn-danger" onclick="eliminarComentario(${c.id})">Eliminar</button>
                </td>
            `;
            tbody.appendChild(fila);
        });

        console.log("✅ Comentarios cargados correctamente");

    } catch (err) {
        console.error("Error cargando comentarios:", err);
    }
}


async function cambiarEstado(id, accion) {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API_ADMIN_COMENTARIOS}/${id}/${accion}`, {
        method: "PUT",
        headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
    });

    if (res.ok) {
        alert(`Comentario ${accion} correctamente`);
        cargarComentarios();
    } else {
        alert("Error al actualizar el comentario");
    }
}

async function eliminarComentario(id) {
    if (!confirm("¿Seguro que deseas eliminar este comentario?")) return;

    const token = localStorage.getItem("token");

    const res = await fetch(`${API_ADMIN_COMENTARIOS}/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (res.ok) {
        alert("Comentario eliminado correctamente");
        cargarComentarios();
    } else {
        alert("Error al eliminar comentario");
    }
}

//////////////////////////////////
async function cargarComentariosDashboard() {
    try {
        const token = localStorage.getItem("token");

        const res = await fetch(API_ADMIN_COMENTARIOS, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) {
            console.error("No autorizado o error al cargar comentarios");
            return;
        }

        const comentarios = await res.json();
        const ul = document.getElementById("dashboardComentarios");

        if (!comentarios || comentarios.length === 0) {
            ul.innerHTML = `<li class="list-group-item text-muted">No hay comentarios</li>`;
            return;
        }

        ul.innerHTML = comentarios.slice(0, 5).map(c => `
            <li class="list-group-item">
                <strong>${c.nombre}</strong>
                <span class="badge bg-${
                    c.estado === 'aprobado'
                        ? 'success'
                        : c.estado === 'rechazado'
                        ? 'danger'
                        : 'warning'
                } float-end">
                    ${c.estado}
                </span>
                <div class="small text-muted mt-1">
                    ${c.texto}
                </div>
            </li>
        `).join("");

    } catch (err) {
        console.error("Error cargando comentarios dashboard:", err);
    }
}
//////////////////////////////////////////////

async function cargarContactos() {
    const token = localStorage.getItem("token");
    if (!token) {
        console.error("No hay token");
        return;
    }

    const res = await fetch(API_ADMIN_CONTACTOS, {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
    });

    if (res.status === 401 || res.status === 403) {
        console.error("No autorizado");
        return;
    }

    if (!res.ok) {
        console.error("Error al cargar contactos");
        return;
    }

    const contactos = await res.json();
    const tbody = document.getElementById("tablaContactos");
    tbody.innerHTML = "";

    contactos.forEach(c => {
    tbody.innerHTML += `
    <tr>
        <td>${c.id}</td>
        <td>${c.nombre}</td>
        <td>${c.email || "-"}</td>
        <td>${c.telefono || "-"}</td>
        <td>${c.asunto || "-"}</td>
        <td>${c.mensaje || "-"}</td>
        <td>${c.leido ? "Leído" : "Nuevo"}</td>
        <td>
            <button onclick="marcarLeido(${c.id}, ${c.leido})">✔</button>
            <button onclick="eliminarContacto(${c.id})">🗑</button>
        </td>
    </tr>`;
});
}


cargarContactos();

/* =============================
ADMIN: marcar como leído/no leído
============================= */
async function marcarLeido(id, leido) {
    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_CONTACTOS}/${id}/leido`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ leido: !leido })
        });

        if (res.ok) {
            cargarContactos();
        } else {
            console.error("No se pudo actualizar el estado");
        }
    } catch (err) {
        console.error("Error de conexión", err);
    }
}

/* =============================
ADMIN: eliminar contacto
============================= */
async function eliminarContacto(id) {
    if (!confirm("¿Seguro que deseas eliminar este contacto?")) return;
    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_CONTACTOS}/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + token }
        });
        if (res.ok) {
            cargarContactos();
        } else {
            console.error("No se pudo eliminar el contacto");
        }
    } catch (err) {
        console.error("Error de conexión", err);
    }
}

/* =============================
Inicializar admin
============================= */
if (document.getElementById('tablaContactos')) {
    cargarContactos(); // solo si estamos en admin
}

// =================== INICIALIZACIÓN ===================
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = 'login';
        return;
    }
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        
        if (payload.rol !== 'admin') {
            alert('No tienes permisos para acceder');
            localStorage.clear();
            window.location.href = 'login';
            return;
        }
    } catch (e) {
        console.error('Token inválido:', e);
        localStorage.clear();
        window.location.href = 'login';
        return;
    }
    

    // Cargar sección inicial
    mostrarSeccion('dashboard');

});

async function verReserva(id) {
console.log("CLICK VER RESERVA ID:", id);

    const token = localStorage.getItem("token");

    try {
        const res = await fetch(`${API_RESERVAS}/${id}`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) {
            crearToast("No se pudo cargar la reserva", "danger");
            return;
        }

        const r = await res.json();

        document.getElementById("detalleReserva").innerHTML = `
            <div class="row g-3">

                <div class="col-md-6">
                    <strong>Cliente:</strong><br>
                    ${r.nombre || "No disponible"}
                </div>

                <div class="col-md-6">
                    <strong>Email:</strong><br>
                    ${r.email || "-"}
                </div>

                <div class="col-md-6">
                    <strong>Teléfono:</strong><br>
                    ${r.telefono || "-"}
                </div>

                <div class="col-md-6">
                    <strong>Habitación:</strong><br>
                    ${r.habitacion?.nombre || "-"}
                </div>

                <div class="col-md-6">
                    <strong>Fecha entrada:</strong><br>
                    ${r.fecha_entrada}
                </div>

                <div class="col-md-6">
                    <strong>Fecha salida:</strong><br>
                    ${r.fecha_salida}
                </div>

                <div class="col-md-6">
                    <strong>Personas:</strong><br>
                    ${r.num_personas}
                </div>

                <div class="col-md-6">
                    <strong>Precio total:</strong><br>
                    $${r.precio_total}
                </div>

                <div class="col-md-6">
                    <strong>Estado:</strong><br>
                    <span class="badge bg-${r.estado === 'confirmada' ? 'success' : r.estado === 'cancelada' ? 'danger' : 'warning'}">
                        ${r.estado}
                    </span>
                </div>

                <div class="col-md-12">
                    <strong>Mensaje del cliente:</strong>
                    <div class="border rounded p-2 mt-1 bg-light">
                        ${r.notas || "Sin notas"}
                    </div>
                </div>

            </div>
        `;

        new bootstrap.Modal(document.getElementById("modalReserva")).show();

    } catch (err) {
        console.error(err);
        crearToast("Error de conexión", "danger");
    }
}

function subirPortada() {
    const input = document.getElementById("portada");
    const file = input.files[0];

    if (!file) {
        alert("Selecciona una imagen");
        return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
        alert("Sesión no válida");
        return;
    }

    const formData = new FormData();
    formData.append("imagen", file);

    fetch(`${API_ADMIN_PORTADA}`, {

    method: "POST",
    headers: {
        "Authorization": "Bearer " + token
    },
    body: formData
})
.then(res => res.json())
.then(data => {
    console.log(data);
    alert("Portada actualizada correctamente");
})
.catch(err => {
    console.error(err);
    alert("Error al subir la imagen");
});
}
