
document.addEventListener('DOMContentLoaded', function() {
    const tabla = document.querySelector('.devices-table');
    const modal = document.getElementById('modalConfirmacion');
    let productoAEliminar = null;

    // Función para hacer un campo editable
function hacerEditable(td) {
    const valor = td.textContent.trim();
    const campo = td.dataset.field;
    let input;

    if (campo === 'tipo') {
        input = document.createElement('select');
        const opciones = ['Smartphone', 'Tablet', 'Laptop', 'Smartwatch'];
        opciones.forEach(opcion => {
            const option = document.createElement('option');
            option.value = opcion;
            option.textContent = opcion;
            option.selected = opcion === valor;
            input.appendChild(option);
        });
    } else if (campo === 'sistema_operativo') {  // Corregido el nombre del campo
        input = document.createElement('select');
        const opciones = ['Android', 'iOS', 'Windows', 'macOS'];
        opciones.forEach(opcion => {
            const option = document.createElement('option');
            option.value = opcion;
            option.textContent = opcion;
            option.selected = opcion === valor;
            input.appendChild(option);
        });
    } else {
        input = document.createElement('input');
        input.type = campo === 'precio' ? 'number' : 'text';
        if (campo === 'precio') input.step = '0.01';
        input.value = valor;
    }

    td.textContent = '';
    td.appendChild(input);
    td.classList.add('editing');
}


    // Función para guardar cambios
async function guardarCambios(tr) {
    const productoId = tr.dataset.productoId;
    const datos = new FormData();
    const editableCells = tr.querySelectorAll('.editable.editing');

    editableCells.forEach(cell => {
        const input = cell.querySelector('input, select');
        const fieldName = cell.dataset.field;
        datos.append(fieldName, input.value);
    });

    try {
        const response = await fetch(`/update_device/${productoId}/`, {
            method: 'POST',
            body: datos,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            await response.json();
            editableCells.forEach(cell => {
                const input = cell.querySelector('input, select');
                cell.textContent = input.value;
                cell.classList.remove('editing');
            });

            const btnGuardar = tr.querySelector('.btn-guardar');
            const btnEditar = tr.querySelector('.btn-editar');
            btnGuardar.style.display = 'none';
            btnEditar.style.display = 'inline-block';

            mostrarMensaje('Producto actualizado con éxito', 'success');
        } else {
            mostrarMensaje('Error al actualizar el producto', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al actualizar el producto', 'error');
    }
}


    // Event listeners
    tabla.addEventListener('click', async (e) => {
        const target = e.target;
        const tr = target.closest('tr');

        if (!tr) return;

        if (target.closest('.btn-editar')) {
            const btnGuardar = tr.querySelector('.btn-guardar');
            const btnEditar = tr.querySelector('.btn-editar');

            tr.querySelectorAll('.editable').forEach(td => hacerEditable(td));
            btnGuardar.style.display = 'inline-block';
            btnEditar.style.display = 'none';
        }

        if (target.closest('.btn-guardar')) {
            await guardarCambios(tr);
            const btnGuardar = tr.querySelector('.btn-guardar');
            const btnEditar = tr.querySelector('.btn-editar');
            btnGuardar.style.display = 'none';
            btnEditar.style.display = 'inline-block';
        }

        if (target.closest('.btn-eliminar')) {
            productoAEliminar = tr;
            modal.style.display = 'block';
        }
    });

    // Eventos del modal
    document.getElementById('confirmarEliminar').addEventListener('click', async () => {
        if (productoAEliminar) {
            const productoId = productoAEliminar.dataset.productoId;
            try {
                const response = await fetch(`/delete_device/${productoId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                if (response.ok) {
                    productoAEliminar.remove();
                    mostrarMensaje('Producto eliminado con éxito', 'success');
                } else {
                    mostrarMensaje('Error al eliminar');
                }
            } catch (error) {
                mostrarMensaje('Error al eliminar el producto', 'error');
            }
        }
        modal.style.display = 'none';
    });

    document.getElementById('cancelarEliminar').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Función auxiliar para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Función para mostrar mensajes
    function mostrarMensaje(mensaje, tipo) {
        // Implementa tu propia lógica de mostrar mensajes
        console.log(`${tipo}: ${mensaje}`);
    }
});