class FilterManager {
    constructor() {
        this.isAuthenticated = document.body.classList.contains('user-authenticated');
        this.initializeDOMElements();
        this.initializeEventListeners();
        this.restaurarFiltrosGuardados();
    }

    initializeDOMElements() {
        this.elements = {
            productosGrid: document.querySelector('.productos-grid'),
            confirmarFiltros: document.getElementById('confirmar-filtros'),
            reiniciarFiltros: document.getElementById('reiniciar-filtros'),
            categoriaCheckboxes: document.querySelectorAll('input[name="tipo"]'),
            soCheckboxes: document.querySelectorAll('input[name="sistema_operativo"]'),
            precioMin: document.getElementById('precio_min'),
            precioMax: document.getElementById('precio_max')
        };
    }

    initializeEventListeners() {
        if (this.elements.confirmarFiltros) {
            this.elements.confirmarFiltros.addEventListener('click', () => this.aplicarFiltros());
        }

        if (this.elements.reiniciarFiltros) {
            this.elements.reiniciarFiltros.addEventListener('click', () => this.reiniciarFiltros());
        }

        // Event listeners para inputs de precio
        if (this.elements.precioMin) {
            this.elements.precioMin.addEventListener('change', () => this.aplicarFiltros());
        }
        if (this.elements.precioMax) {
            this.elements.precioMax.addEventListener('change', () => this.aplicarFiltros());
        }

        // Agregar event listeners para el botón de agregar al carrito
        this.elements.productosGrid?.addEventListener('click', (e) => this.manejarAgregarAlCarrito(e));
    }

    getSelectedCheckboxValues(checkboxes) {
        return Array.from(checkboxes || [])
            .filter(cb => cb.checked)
            .map(cb => cb.value);
    }

    async manejarAgregarAlCarrito(e) {
        const button = e.target;
        // Verificar si el elemento clickeado es un botón de agregar al carrito
        if (!button.classList.contains('agregar-al-carrito')) return;

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

    async aplicarFiltros() {
        try {
            const categoriasSeleccionadas = this.getSelectedCheckboxValues(this.elements.categoriaCheckboxes);
            const sosSeleccionados = this.getSelectedCheckboxValues(this.elements.soCheckboxes);
            const precioMin = this.elements.precioMin?.value;
            const precioMax = this.elements.precioMax?.value;

            const params = new URLSearchParams();

            if (categoriasSeleccionadas.length) {
                params.set('tipo', categoriasSeleccionadas.join(','));
            }
            if (sosSeleccionados.length) {
                params.set('sistema_operativo', sosSeleccionados.join(','));
            }
            if (precioMin) params.set('precio_min', precioMin);
            if (precioMax) params.set('precio_max', precioMax);
            params.set('_', Date.now());

            const newUrl = `${window.location.pathname}?${params.toString()}`;
            const headers = new Headers({
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html'
            });

            if (this.isAuthenticated) {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                if (csrfToken) headers.append('X-CSRFToken', csrfToken);
            }

            const response = await fetch(newUrl, {
                method: 'GET',
                credentials: 'same-origin',
                headers: headers
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const htmlText = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlText, 'text/html');
            const nuevaGrid = doc.querySelector('.productos-grid');

            if (nuevaGrid && this.elements.productosGrid) {
                this.elements.productosGrid.innerHTML = nuevaGrid.innerHTML;
            }

            this.guardarFiltros({
                categorias: categoriasSeleccionadas,
                sistemasOperativos: sosSeleccionados,
                precioMin: precioMin,
                precioMax: precioMax
            });

        } catch (error) {
            if (this.elements.productosGrid) {
                const errorMessage = document.createElement('div');
                errorMessage.className = 'error-mensaje';
                errorMessage.textContent = 'Error al cargar los productos. Por favor, intente nuevamente.';
                this.elements.productosGrid.innerHTML = '';
                this.elements.productosGrid.appendChild(errorMessage);
            }
        }
    }

    reiniciarFiltros() {
        // Reiniciar checkboxes
        this.elements.categoriaCheckboxes?.forEach(cb => cb.checked = false);
        this.elements.soCheckboxes?.forEach(cb => cb.checked = false);

        // Reiniciar valores de precio
        if (this.elements.precioMin) this.elements.precioMin.value = '0';
        if (this.elements.precioMax) this.elements.precioMax.value = '10000';

        // Reiniciar slider
        if (window.priceRangeSlider) {
            window.priceRangeSlider.sliderMin.value = window.priceRangeSlider.minValue;
            window.priceRangeSlider.sliderMax.value = window.priceRangeSlider.maxValue;
            window.priceRangeSlider.updateSliderValues();
        }

        localStorage.removeItem('filtros');
        this.aplicarFiltros();
    }

    guardarFiltros(filtros) {
        localStorage.setItem('filtros', JSON.stringify(filtros));
    }

    restaurarFiltrosGuardados() {
        const filtrosGuardados = localStorage.getItem('filtros');
        if (!filtrosGuardados) return;

        const filtros = JSON.parse(filtrosGuardados);

        filtros.categorias?.forEach(categoria => {
            const checkbox = Array.from(this.elements.categoriaCheckboxes || [])
                .find(cb => cb.value === categoria);
            if (checkbox) checkbox.checked = true;
        });

        filtros.sistemasOperativos?.forEach(so => {
            const checkbox = Array.from(this.elements.soCheckboxes || [])
                .find(cb => cb.value === so);
            if (checkbox) checkbox.checked = true;
        });

        if (this.elements.precioMin) this.elements.precioMin.value = filtros.precioMin || '';
        if (this.elements.precioMax) this.elements.precioMax.value = filtros.precioMax || '';
    }

    mostrarNotificacion(message, type) {
        // Método para mostrar notificaciones, implementa según tus necesidades
        console.log(`${type}: ${message}`);
    }

    actualizarTotalCarrito() {
        // Actualizar el total del carrito, implementa según tus necesidades
        console.log("Total carrito actualizado");
    }
}

document.addEventListener('DOMContentLoaded', () => new FilterManager());
