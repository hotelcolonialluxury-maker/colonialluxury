// ==============================
// CONFIGURACIÓN GLOBAL DE RUTAS
// ==============================

// Base automática (http://dominio.com)
const BASE_URL = window.location.origin;

// API base
const API_BASE = `${BASE_URL}/api`;

// ---- AUTH ----
const API_LOGIN = `${API_BASE}/auth/login`;

// ---- ADMIN ----
const API_ADMIN_HABITACIONES = `${API_BASE}/admin/habitaciones`;
const API_ADMIN_CONTACTOS = `${API_BASE}/admin/contactos`;
const API_ADMIN_COMENTARIOS = `${API_BASE}/admin/comentarios`;
const API_ADMIN_RESERVAS = `${API_BASE}/admin/reservas`;
const API_ADMIN_PAGOS = `${API_BASE}/admin/pagos`;
const API_ADMIN_PORTADA = `${API_BASE}/admin/portada`;

// ---- PUBLIC / COMÚN ----
const API_HABITACIONES = `${API_BASE}/habitaciones`;
const API_RESERVAS = `${API_BASE}/reservas`;
const API_PAGOS = `${API_BASE}/pagos`;
const API_CONTACTOS = `${API_BASE}/contactos`;
const API_COMENTARIOS = `${API_BASE}/comentarios`;
const API_PORTADA = `${API_BASE}/portada`;
