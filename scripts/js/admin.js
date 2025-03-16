document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos
    const addDeviceForm = document.getElementById('addDeviceForm');
    document.getElementById('toggleAddForm');
    const fileInput = document.getElementById('imagen');
    const fileButton = document.querySelector('.file-selector-button');
    const fileName = document.querySelector('.file-name');
    const imagePreview = document.getElementById('imagePreview');

    // Manejo de selección de archivo mejorado
fileButton?.addEventListener('click', (e) => {
    e.preventDefault();
    fileInput.click();
});


    fileInput?.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            fileName.textContent = file.name;

            // Validación del tipo de archivo
            if (!file.type.startsWith('image/')) {
                showNotification('Por favor, selecciona un archivo de imagen válido', 'error');
                this.value = '';
                fileName.textContent = 'Ningún archivo seleccionado';
                if (imagePreview) {
                    imagePreview.style.display = 'none';
                }
                return;
            }

            // Preview de la imagen
            const reader = new FileReader();
            reader.onload = function(e) {
                if (imagePreview) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        } else {
            fileName.textContent = 'Ningún archivo seleccionado';
            if (imagePreview) {
                imagePreview.style.display = 'none';
            }
        }
    });

       // Manejo del formulario de añadir dispositivo
    addDeviceForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Iniciando envío del formulario...');

        const formData = new FormData(this);
        const requiredFields = ['nombre', 'descripcion', 'precio', 'stock', 'tipo', 'sistema'];
        let isValid = true;

        // Log de los datos del formulario
        console.log('Campo descripción:', formData.get('descripcion'));
        console.log('Datos del formulario:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }

        for (let field of requiredFields) {
            const value = formData.get(field);
            if (!value) {
                showNotification(`El campo ${field} es obligatorio`, 'error');
                isValid = false;
                break;
            }
        }

        if (!isValid) return;

        const getCookie = () => {
            return "";
        };
        try {
            console.log('Enviando solicitud al servidor...');

            const response = await fetch('/admin/add-device/', { // URL corregida
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie(),
                }
            });

            console.log('Respuesta recibida:', response.status);

            const contentType = response.headers.get('content-type');
            let result;

if (contentType && contentType.includes('application/json')) {
    result = await response.json();
} else {
    const text = await response.text();
    console.log('Respuesta no JSON:', text);
    return {
        success: false,
        message: 'Respuesta del servidor no válida',
        data: text
    };
}

if (!response.ok) {
    return {
        success: false,
        status: response.status,
        message: result.message || 'Error al añadir el dispositivo',
        data: result
    };
}


            showNotification(result.message || 'Dispositivo añadido correctamente', 'success');
            setTimeout(() => location.reload(), 1500);

        } catch (error) {
            console.error('Error durante el envío:', error);
            showNotification('Error: ' + error.message, 'error');
        }
    });

    // Función para mostrar notificaciones
    function showNotification(message, type) {
        console.log(`Notificación: ${type} - ${message}`); // Debug log

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});

// Para mostrar el modal
function showModal() {
    const modal = document.getElementById('modalConfirmacion');
    modal.classList.add('show');
}

// Para ocultar el modal
function hideModal() {
    const modal = document.getElementById('modalConfirmacion');
    modal.classList.add('closing');
    setTimeout(() => {
        modal.classList.remove('show', 'closing');
    }, 300);
}

// Eventos para los botones
document.getElementById('cancelarEliminar').addEventListener('click', hideModal);
