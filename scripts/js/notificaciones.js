// Verificamos si ya existe una instancia
if (!window.SistemaNotificaciones) {
    window.SistemaNotificaciones = class {
        constructor() {
            this.contenedor = document.getElementById('sistema-notificaciones');
            if (!this.contenedor) {
                this.contenedor = document.createElement('div');
                this.contenedor.id = 'sistema-notificaciones';
                document.body.appendChild(this.contenedor);
            }
        }

        mostrar(mensaje, tipo = 'info', duracion = 3000) {
            const notificacion = document.createElement('div');
            notificacion.className = `notificacion ${tipo}`;
            notificacion.textContent = mensaje;
            
            const btnCerrar = document.createElement('button');
            btnCerrar.innerHTML = '×';
            btnCerrar.style.cssText = `
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 0 5px;
            `;
            notificacion.style.position = 'relative';
            notificacion.style.paddingRight = '30px';
            notificacion.appendChild(btnCerrar);
            
            this.contenedor.appendChild(notificacion);

            btnCerrar.addEventListener('click', () => {
                this.cerrarNotificacion(notificacion);
            });

            setTimeout(() => {
                if (notificacion.parentElement) {
                    this.cerrarNotificacion(notificacion);
                }
            }, duracion);
        }

        cerrarNotificacion(notificacion) {
            notificacion.style.animation = 'fadeOut 0.3s forwards';
            setTimeout(() => {
                if (notificacion.parentElement === this.contenedor) {
                    this.contenedor.removeChild(notificacion);
                }
            }, 300);
        }

        success(mensaje, duracion = 3000) {
            this.mostrar(mensaje, 'success', duracion);
        }

        error(mensaje, duracion = 3000) {
            this.mostrar(mensaje, 'error', duracion);
        }

        info(mensaje, duracion = 3000) {
            this.mostrar(mensaje, 'info', duracion);
        }
    };
}

// Creamos la instancia global solo si no existe
if (!window.notificaciones) {
    window.notificaciones = new window.SistemaNotificaciones();
}