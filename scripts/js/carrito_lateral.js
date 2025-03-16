document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('.btn-abrir-carrito').addEventListener('click', (e) => {
    e.preventDefault();
    window.carritoLateral.abrir();
});

    // Configuración del carrito
    const carritoConfig = {
        elementos: {
            carritoLateral: document.getElementById('carrito-lateral'),
            overlay: document.getElementById('overlay'),
            btnCerrarCarrito: document.getElementById('cerrar-carrito'),
            btnPagar: document.getElementById('btn-pagar'),
            productosContainer: document.getElementById('productos-carrito'),
            totalElement: document.getElementById('total-carrito')
        },
        urls: {
            obtenerCarrito: '/api/carrito/',
            actualizarProducto: (id) => `/api/carrito/actualizar/${id}/`,
            eliminarProducto: (id) => `/api/carrito/eliminar/${id}/`
        }
    };

    // Funciones de utilidad
    function actualizarTotal(total) {
        if (carritoConfig.elementos.totalElement) {
            carritoConfig.elementos.totalElement.textContent = `$${parseFloat(total).toFixed(2)}`;
        }
    }

    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Funciones principales del carrito
    async function actualizarCarrito() {
        try {
            const response = await fetch(carritoConfig.urls.obtenerCarrito);
            if (!response.ok) throw new Error('Error al obtener datos del carrito');

            const datos = await response.json();
            renderizarProductos(datos.productos);
            actualizarTotal(datos.total);
        } catch (error) {
            window.notificaciones.mostrarNotificacion('Error al cargar el carrito', 'error');
            console.error('Error:', error);
        }
    }

    function renderizarProductos(productos) {
        const { productosContainer } = carritoConfig.elementos;
        if (!productosContainer) return;

        productosContainer.innerHTML = '';
        const template = document.getElementById('producto-carrito-template');

        if (!template) {
            console.error('Template no encontrado');
            return;
        }

        productos.forEach(producto => {
            const productoElement = crearElementoProducto(producto, template);
            productosContainer.appendChild(productoElement);
        });
    }

    function crearElementoProducto(producto, template) {
        const clon = template.content.cloneNode(true);
        const productoContainer = clon.querySelector('.producto-carrito');

        if (!productoContainer) return clon;

        // Configurar datos del producto
        productoContainer.dataset.productoId = producto.id;

        // Actualizar elementos del producto
        const elementos = {
            imagen: clon.querySelector('.producto-imagen'),
            nombre: clon.querySelector('.producto-nombre'),
            precio: clon.querySelector('.producto-precio'),
            cantidad: clon.querySelector('.cantidad')
        };

        if (elementos.imagen) elementos.imagen.src = producto.imagen;
        if (elementos.nombre) elementos.nombre.textContent = producto.nombre;
        if (elementos.precio) elementos.precio.textContent = `$${producto.precio}`;
        if (elementos.cantidad) elementos.cantidad.textContent = producto.cantidad;

        // Configurar botones
        const botones = {
            decrementar: clon.querySelector('[data-accion="decrementar"]'),
            incrementar: clon.querySelector('[data-accion="incrementar"]'),
            eliminar: clon.querySelector('.btn-eliminar')
        };

        if (botones.decrementar) {
            botones.decrementar.addEventListener('click', () =>
                actualizarCantidadProducto(producto.id, parseInt(elementos.cantidad.textContent) - 1));
        }

        if (botones.incrementar) {
            botones.incrementar.addEventListener('click', () =>
                actualizarCantidadProducto(producto.id, parseInt(elementos.cantidad.textContent) + 1));
        }

        if (botones.eliminar) {
            botones.eliminar.addEventListener('click', () => eliminarProducto(producto.id));
        }

        return clon;
    }

    async function actualizarCantidadProducto(productoId, nuevaCantidad) {
        if (nuevaCantidad < 1) return;

        try {
            const response = await fetch(carritoConfig.urls.actualizarProducto(productoId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ cantidad: nuevaCantidad })
            });

            if (!response.ok) throw new Error('Error en la respuesta del servidor');

            const data = await response.json();
            if (data.success) {
                actualizarCarrito();
                //window.notificaciones.mostrar('Cantidad actualizada', 'success');
            }
        } catch (error) {
            //window.notificaciones.mostrar('Error al actualizar cantidad', 'error');
            console.error('Error:', error);
        }
    }

    async function eliminarProducto(productoId) {
        try {
            const response = await fetch(carritoConfig.urls.eliminarProducto(productoId), {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (!response.ok) throw new Error('Error al eliminar el producto');

            const data = await response.json();
            if (data.success) {
                actualizarCarrito();
                //window.notificaciones.mostrar('Producto eliminado', 'success');
            }
        } catch (error) {
            //window.notificaciones.mostrar('Error al eliminar producto', 'error');
            console.error('Error:', error);
        }
    }

    // Funciones de control del carrito
    function abrirCarrito() {
        carritoConfig.elementos.carritoLateral.classList.add('abierto');
        carritoConfig.elementos.overlay.classList.add('activo');
        actualizarCarrito();
    }

    function cerrarCarrito() {
        carritoConfig.elementos.carritoLateral.classList.remove('abierto');
        carritoConfig.elementos.overlay.classList.remove('activo');
        location.reload();
    }

    // Event Listeners
    carritoConfig.elementos.btnCerrarCarrito?.addEventListener('click', cerrarCarrito);
    carritoConfig.elementos.overlay?.addEventListener('click', cerrarCarrito);
    carritoConfig.elementos.btnPagar?.addEventListener('click', () => window.location.href = '/checkout/');

    // Exportar funciones para uso global
    window.carritoLateral = {
        abrir: abrirCarrito,
        cerrar: cerrarCarrito,
        actualizar: actualizarCarrito
    };

    // Inicialización automática si el carrito está abierto
    if (carritoConfig.elementos.carritoLateral?.classList.contains('abierto')) {
        actualizarCarrito();
    }
});
