document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const profileButton = document.getElementById('profileButton');
    const profileMenu = document.getElementById('profileMenuContainer');
    const showProfileForm = document.getElementById('showProfileForm');
    const profileForm = document.getElementById('profileForm');
    const deleteProfileBtn = document.getElementById('deleteProfile');
    const logoutForm = document.getElementById('logoutForm');
document.body.style.zoom = "90%";

    // Manejo del menú de perfil
    if (profileButton && profileMenu) {
        profileButton.addEventListener('click', function(e) {
            e.stopPropagation();
            profileMenu.classList.toggle('active');
        });

        document.addEventListener('click', function(e) {
            if (!profileMenu.contains(e.target) && !profileButton.contains(e.target)) {
                profileMenu.classList.remove('active');
            }
        });
    }

    // Manejo del formulario de logout
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            e.preventDefault();

            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    throw new Error('Error en el logout');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al cerrar sesión');
            });
        });
    }

    // Mostrar/ocultar formulario de perfil
    if (showProfileForm && profileForm) {
        showProfileForm.addEventListener('click', function() {
            const isHidden = profileForm.style.display === 'none';
            profileForm.style.display = isHidden ? 'block' : 'none';
            showProfileForm.classList.toggle('active');
        });
    }

    // Confirmar eliminación de perfil
    if (deleteProfileBtn) {
        deleteProfileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('¿Estás seguro de que deseas eliminar tu perfil? Esta acción no se puede deshacer.')) {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

                if (!csrfToken) {
                    console.error('No se encontró el token CSRF');
                    return;
                }

                fetch('/delete-profile/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken.value,
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la respuesta del servidor');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        window.location.href = '/account/';
                    } else {
                        throw new Error(data.message || 'Error al eliminar el perfil');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al eliminar el perfil: ' + error.message);
                });
            }
        });
    }
});