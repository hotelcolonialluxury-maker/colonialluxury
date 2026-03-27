document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const alerta = document.getElementById('alerta');
    
    alerta.classList.add('d-none');

    try {
        const res = await fetch(API_LOGIN, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alerta.textContent = data.error || 'Error al iniciar sesión';
            alerta.classList.remove('d-none');
        } else {
            localStorage.setItem('token', data.token);
            localStorage.setItem('usuario', JSON.stringify(data.usuario));
            
            if (data.usuario.rol === 'admin') {
                window.location.href = '/admin';
            } else {
                alerta.textContent = 'No tienes permisos de administrador';
                alerta.classList.remove('d-none');
                localStorage.clear();
            }
        }

    } catch (err) {
        alerta.textContent = 'Error de conexión con el servidor';
        alerta.classList.remove('d-none');
    }
});