document.addEventListener('DOMContentLoaded', function () {
    const stockSwitch = document.querySelector('input[name="con_stock"]');
    const cards = document.querySelectorAll('.card');

    // Función para manejar la visibilidad de las cards
    function handleStockVisibility() {
        cards.forEach(card => {
            if (stockSwitch.checked && card.classList.contains('out-of-stock-card')) {
                card.classList.add('hidden-card');
            } else {
                card.classList.remove('hidden-card');
            }
        });
    }

    // Aplicar el filtro inicial si el switch está activado
    if (stockSwitch) {
        if (stockSwitch.checked) {
            handleStockVisibility();
        }

        // Escuchar cambios en el switch
        stockSwitch.addEventListener('change', handleStockVisibility);
    }
});