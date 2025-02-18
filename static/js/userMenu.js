function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    menu.classList.toggle('active');
}

function showChangeEmailForm() {
    // You can implement this function to show a modal or form
    // for changing the email address
    alert('Esta función estará disponible próximamente');
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById('userMenu');
    const userBtn = document.querySelector('.user-profile-btn');

    if (!menu.contains(e.target) && !userBtn.contains(e.target)) {
        menu.classList.remove('active');
    }
});