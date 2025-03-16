// carrito.js
'use strict';

if (typeof window.CarritoManager === 'undefined') {
    window.CarritoManager = class {
        constructor() {
            this.csrftoken = null;
            this.actualizacionEnProceso = false;
            this.tiempoMinEntrePeticiones = 500;
            this.ultimaOperacion = {
                tiempo: 0,
                productoId: null,
                operacion: null
            };
        }

        /**
         * Inicializa el gestor del carrito
         */
        inicializar() {
            try {
                if (window.carritoInicializado) {
                    return false;
                }
                window.carritoInicializado = true;

                const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
                if (!tokenElement) {
                    console.error('Error: Token CSRF no encontrado');
                    return false;
                }
                this.csrftoken = tokenElement.value;
                this.inicializarEventos();
                this.inicializarEventosAgregarCarrito(); // Añadir esta línea
                return true;
            } catch (error) {
                console.error('Error al inicializar el carrito:', error);
                return false;
            }
        }

        /**
         * Configura los event listeners del carrito
         */
        inicializarEventos() {
            const productosCarrito = document.getElementById('productos-carrito');
            if (productosCarrito) {
                productosCarrito.addEventListener('click', (e) => this.manejarEventosCarrito(e));
            }
        }

        /**
         * Verifica si una operación es duplicada
         */
        esOperacionDuplicada(productoId, operacion) {
            const ahora = Date.now();
            if (this.ultimaOperacion.productoId === productoId &&
                this.ultimaOperacion.operacion === operacion &&
                ahora - this.ultimaOperacion.tiempo < this.tiempoMinEntrePeticiones) {
                return true;
            }

            this.ultimaOperacion = {
                tiempo: ahora,
                productoId: productoId,
                operacion: operacion
            };
            return false;
        }

        /**
         * Maneja los eventos del carrito
         */
        async manejarEventosCarrito(e) {
            e.preventDefault();
            e.stopPropagation();

            const boton = e.target;
            const accion = boton.dataset.accion;

            // Si no es un botón con acción o está en proceso, ignorar
            if (!accion || this.actualizacionEnProceso) return;

            const productoContainer = boton.closest('.producto-carrito');
            if (!productoContainer) return;

            const productoId = productoContainer.dataset.productoId;
            const cantidadElement = productoContainer.querySelector('.cantidad');
            if (!cantidadElement) return;

            const cantidad = parseInt(cantidadElement.textContent, 10);
            if (isNaN(cantidad)) return;

            // Verificar operación duplicada
            if (this.esOperacionDuplicada(productoId, accion)) {
                return;
            }

            // Manejar las diferentes acciones
            switch (accion) {
                case 'incrementar':
                    await this.actualizarCantidadCarrito(productoId, cantidad + 1, cantidadElement);
                    break;
                case 'decrementar':
                    if (cantidad > 1) {
                        await this.actualizarCantidadCarrito(productoId, cantidad - 1, cantidadElement);
                    } else {
                        this.mostrarNotificacion('La cantidad no puede ser menor a 1', 'error');
                    }
                    break;
                default:
                    if (boton.closest('.btn-eliminar')) {
                        await this.eliminarProducto(productoId, productoContainer);
                    }
            }
        }

        /**
         * Actualiza la cantidad de un producto en el carrito
         */
        async actualizarCantidadCarrito(productoId, nuevaCantidad, cantidadElement) {
            if (this.actualizacionEnProceso) {
            console.log('Operación en proceso, esperando...');
            return;
        }
            try {
                this.actualizacionEnProceso = true;
                cantidadElement.disabled = true;

                console.log(`Intentando actualizar producto ${productoId} a cantidad ${nuevaCantidad}`);

                const response = await fetch(`/api/carrito/actualizar/${productoId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.csrftoken,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ cantidad: nuevaCantidad }),
                    credentials: 'same-origin'
                });

                console.log('Status de respuesta:', response.status);
                const data = await response.json();
                console.log('Datos recibidos:', data);

                if (!response.ok) {
                    throw new Error(`Error del servidor: ${data.error || response.statusText}`);
                }

                if (data.success) {
                    console.log(`Actualizando cantidad a ${data.nueva_cantidad}`);
                    cantidadElement.textContent = data.nueva_cantidad;
                    this.actualizarTotalCarrito();
                    this.mostrarNotificacion('Cantidad actualizada', 'success');
                } else {
                    // Si hay un error específico en la respuesta, lo mostramos
                    const errorMessage = data.error || 'Error al actualizar la cantidad';
                    console.warn('Error en la actualización:', errorMessage);
                    this.mostrarNotificacion(errorMessage, 'error');
                }
            } catch (error) {
                console.error('Error en la operación:', error);
                this.mostrarNotificacion(
                    error.message || 'Error al actualizar cantidad',
                    'error'
                );
            } finally {
                // Aseguramos que el elemento se rehabilite después del tiempo mínimo
                setTimeout(() => {
                    this.actualizacionEnProceso = false;
                    cantidadElement.disabled = false;
                    console.log('Operación completada, control habilitado');
                }, this.tiempoMinEntrePeticiones);
            }
        }

        /**
         * Elimina un producto del carrito
         */
        async eliminarProducto(productoId, productoContainer) {
            if (this.actualizacionEnProceso) return;

            try {
                this.actualizacionEnProceso = true;
                productoContainer.style.opacity = '0.5';

                const response = await fetch(`/api/carrito/eliminar/${productoId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.csrftoken,
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                });

                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }

                const data = await response.json();
                if (data.success) {
                    productoContainer.remove();
                    this.actualizarTotalCarrito();
                    this.mostrarNotificacion('Producto eliminado del carrito', 'success');
                } else {
                    productoContainer.style.opacity = '1';
                    this.mostrarNotificacion(data.error || 'Error al eliminar', 'error');
                }
            } catch (error) {
                console.error('Error al eliminar producto:', error);
                this.mostrarNotificacion('Error al eliminar producto', 'error');
                productoContainer.style.opacity = '1';
            } finally {
                setTimeout(() => {
                    this.actualizacionEnProceso = false;
                }, this.tiempoMinEntrePeticiones);
            }
        }

        /**
         * Actualiza el total del carrito
         */
        actualizarTotalCarrito() {
            const totalElement = document.getElementById('total-carrito');
            if (!totalElement) return;

            fetch('/api/carrito/', { credentials: 'same-origin' })
                .then(response => response.json())
                .then(data => {
                    if (data.total !== undefined) {
                        totalElement.textContent = `$${data.total}`;
                    }
                })
                .catch(error => {
                    console.error('Error al actualizar total:', error);
                });
        }

        /**
         * Inicializa los eventos para agregar productos al carrito
         */
        inicializarEventosAgregarCarrito() {
            document.querySelectorAll('.btn-agregar-carrito').forEach(button => {
                button.addEventListener('click', (e) => this.manejarAgregarAlCarrito(e));
            });
        }

        /**
         * Maneja el evento de agregar al carrito
         */
        async manejarAgregarAlCarrito(e) {
            const button = e.target;
            const productoId = button.dataset.productoId;
            const productoInfo = button.closest('.producto-info');
            const stockElement = productoInfo?.querySelector('.stock-cantidad');

            if (!stockElement) return;

            const stockActual = parseInt(stockElement.textContent);

            if (stockActual <= 0) {
                this.mostrarNotificacion('No hay stock disponible', 'error');
                return;
            }

            try {
                const response = await fetch('/agregar-al-carrito/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.csrftoken,
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `producto_id=${productoId}`
                });

                const data = await response.json();

                if (data.success) {
                    stockElement.textContent = data.nuevo_stock;

                    if (data.nuevo_stock <= 0) {
                        button.disabled = true;
                        button.classList.add('sin-stock');
                    }

                    this.mostrarNotificacion('Producto añadido al carrito', 'success');
                    this.actualizarTotalCarrito(); // Actualizar el total del carrito
                } else {
                    this.mostrarNotificacion(data.message || 'Error al añadir al carrito', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                this.mostrarNotificacion('Error al añadir al carrito', 'error');
            }
        }

        /**
         * Muestra notificaciones al usuario
         */
        mostrarNotificacion(mensaje, tipo) {
            if (!window.notificaciones) return;

            switch(tipo) {
                case 'success':
                    window.notificaciones.success(mensaje);
                    break;
                case 'error':
                    window.notificaciones.error(mensaje);
                    break;
                default:
                    window.notificaciones.info(mensaje);
            }
        }
    };
}

// Inicializar cuando el DOM esté listo
if (typeof window.carritoInstance === 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        window.carritoInstance = new window.CarritoManager();
        window.carritoInstance.inicializar();
    });
}