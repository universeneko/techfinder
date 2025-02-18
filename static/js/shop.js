function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    menu.classList.toggle('active');
}

// Cerrar el menú cuando se hace clic fuera de él
document.addEventListener('click', function(event) {
    const userButton = document.querySelector('.user-button');
    const userMenu = document.getElementById('userMenu');

    if (!userButton.contains(event.target) && userMenu.classList.contains('active')) {
        userMenu.classList.remove('active');
    }
});