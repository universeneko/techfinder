from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView
from techfinder import views
from django.conf import settings
from django.conf.urls.static import static
from techfinder.views import get_all_devices

urlpatterns = [
    path('', views.home_view, name='home'),
    path('store/', views.StoreView.as_view(), name='store'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('privacidad/', views.privacidad_view, name='privacidad'),
    path('carrito/agregar/<int:producto_id>/', views.AgregarCarritoView.as_view(), name='agregar_carrito'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('user/', views.user_profile, name='user'),
    path('profile/update/', views.update_user, name='update_user'),
    path('profile/delete/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('admin/', views.AdminView.as_view(), name='admin'),
    path('admin/add_device/', views.add_device, name='add_device'),
    path('update_device/<int:producto_id>/', views.update_device, name='update_device'),
    path('delete_device/<int:producto_id>/', views.delete_device, name='delete_device'),
    path('api/carrito/', views.CarritoApiView.as_view(), name='api_carrito'),
    path('api/carrito/actualizar/<int:producto_id>/', views.ActualizarCarritoApiView.as_view(),
         name='api_actualizar_carrito'),
    path('api/carrito/eliminar/<int:producto_id>/', views.EliminarCarritoApiView.as_view(),
         name='api_eliminar_carrito'),
    path('agregar-al-carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('img/favicon.ico')
    )),
    path('api/cart/count/', views.get_cart_count_api, name='cart_count_api'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/users/', views.get_all_users, name='get_all_users'),
    path('api/admin/add_device/', views.add_device_api, name='add_device_api'),
    path('api/productos/edit/<int:producto_id>/', views.edit_device_api, name='edit_device_api'),
    path('api/productos/delete/<int:producto_id>/', views.delete_device_api, name='delete_device_api'),
    path('api/devices/', get_all_devices, name='get_all_devices'),
    path('api/devices/<int:id>/', views.get_device_by_id, name='get_device_by_id'),
]

# Añadir las URLs de archivos estáticos y media solo en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
