document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.custom-alert');

    alerts.forEach(alert => {
        // Configurar el tiempo de desaparición automática (5 segundos)
        setTimeout(() => {
            alert.classList.add('alert-dismiss');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);

        // Manejar el botón de cerrar
        const closeButton = alert.querySelector('.btn-close-custom');
        closeButton.addEventListener('click', () => {
            alert.classList.add('alert-dismiss');
            setTimeout(() => {
                alert.remove();
            }, 500);
        });
    });
});