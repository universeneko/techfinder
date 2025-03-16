function updateCartBadge() {
    fetch('/api/cart/count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.cart-badge');  // Ajusta el selector según tu HTML
            if (badge) {
                badge.textContent = data.count;
                // Si el contador es 0, puedes ocultarlo
                badge.style.display = data.count > 0 ? 'block' : 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}

// Llamar a updateCartBadge después de agregar al carrito
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar badge al cargar la página
    updateCartBadge();

    // Agregar el listener a los botones de agregar al carrito
    const addToCartButtons = document.querySelectorAll('.add-to-cart-button');  // Ajusta el selector según tu HTML
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Después de que la solicitud de agregar al carrito sea exitosa
            updateCartBadge();
        });
    });
});