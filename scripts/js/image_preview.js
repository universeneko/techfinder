document.addEventListener('DOMContentLoaded', function() {
    // Vista previa de imagen
    const imageInput = document.getElementById('imagen');
    const imagePreview = document.getElementById('imagePreview').querySelector('img');
    const fileNameDisplay = document.querySelector('.file-name');
    const form = document.getElementById('addDeviceForm');

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileNameDisplay.textContent = file.name;
            const reader = new FileReader();
            reader.onload = function(e) {
                if (typeof e.target.result === 'string') {
                    imagePreview.src = e.target.result;
                }
                imagePreview.style.display = 'block';
            }
            reader.readAsDataURL(file);
        } else {
            fileNameDisplay.textContent = 'Ningún archivo seleccionado';
            imagePreview.style.display = 'none';
        }
    });

    // Botón selector de archivo personalizado
    document.querySelector('.file-selector-button').addEventListener('click', function() {
        imageInput.click();
    });

    // Toggle del formulario
    const toggleBtn = document.getElementById('toggleAddForm');
    const addForm = document.getElementById('addDeviceForm');

    toggleBtn.addEventListener('click', function() {
        addForm.classList.toggle('collapsed');
        this.querySelector('i').classList.toggle('fa-chevron-up');
        this.querySelector('i').classList.toggle('fa-chevron-down');
    });

    // Manejo del envío del formulario
form.addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch('/admin/add_device/', {  // Modificada la URL para que coincida con urls.py
        method: 'POST',
        body: formData,
        credentials: 'same-origin'  // Esto asegura que las cookies se envíen
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error de red o servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Limpiar el formulario
            form.reset();
            imagePreview.style.display = 'none';
            fileNameDisplay.textContent = 'Ningún archivo seleccionado';

            // Mostrar mensaje de éxito
            alert('Dispositivo añadido correctamente');

            // Recargar la página para mostrar el nuevo dispositivo
            window.location.reload();
        } else {
            alert(data.message || 'Error al añadir el dispositivo');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud: ' + error.message);
    });
});
});
