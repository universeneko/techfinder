// Constantes para URLs
const LOGIN_URL = '/login/';
const REGISTER_URL = '/register/';
const SHOP_URL = '/shop/';

// Función para cambiar entre tabs
function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.tab:${tab === 'login' ? 'first-child' : 'last-child'}`).classList.add('active');

    document.querySelectorAll('.form-container').forEach(f => f.classList.remove('active'));
    document.getElementById(`${tab}Form`).classList.add('active');
}

// Función unificada para mostrar mensajes
function showMessage(message, isError = false) {
    const formContainer = document.querySelector('.form-container.active');
    let messageContainer = formContainer.querySelector('.message-container');

    // Si no existe el contenedor de mensajes, lo creamos
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';
        formContainer.insertBefore(messageContainer, formContainer.firstChild);
    }

    messageContainer.textContent = message;
    messageContainer.className = `message-container ${isError ? 'error' : 'success'}`;
}

// Manejador del formulario de registro
async function handleRegister(event) {
    event.preventDefault();

    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    // Validación
    if (!name || !email || !password) {
        showMessage('Por favor complete todos los campos', true);
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('password', password);

    try {
        const response = await fetch(REGISTER_URL, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Accept': 'application/json',
            },
            body: formData,
            credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Registro exitoso. Redirigiendo al login...', false);
            setTimeout(() => {
                window.location.href = LOGIN_URL;
            }, 2000);
        } else {
            showMessage(data.error || 'Error en el registro', true);
        }
    } catch (error) {
        console.error('Error en el registro:', error);
        showMessage('Error en el registro. Por favor intente nuevamente.', true);
    }
}

// Manejador del formulario de login
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();

    // Validación
    if (!username || !password) {
        showMessage('Por favor complete todos los campos', true);
        return;
    }

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(LOGIN_URL, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Login exitoso. Redirigiendo...', false);
            setTimeout(() => {
                window.location.href = SHOP_URL;
            }, 1000);
        } else {
            showMessage(data.error || 'Error en el inicio de sesión', true);
        }
    } catch (error) {
        console.error('Error en el login:', error);
        showMessage('Error al procesar la solicitud', true);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Listeners para los tabs si existen
    const loginTab = document.querySelector('.tab[data-tab="login"]');
    const registerTab = document.querySelector('.tab[data-tab="register"]');

    if (loginTab) {
        loginTab.addEventListener('click', () => switchTab('login'));
    }

    if (registerTab) {
        registerTab.addEventListener('click', () => switchTab('register'));
    }
});