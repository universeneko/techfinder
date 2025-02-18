from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from backend.views import error_404_view
from devices import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("devices.urls")),
    path("shop/", views.shop, name="shop"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path("manage/", views.manage, name="manage"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path('api/products', views.ProductList.as_view(), name='product-list'),
    path('logout/', views.logout_view, name='logout'),
    path('guest-login/', views.guest_login, name='guest_login'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:dispositivo_id>/', views.add_to_cart, name='add_to_cart'),

]

# Agregar configuración de archivos estáticos y media en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Asignamos nuestra vista personalizada
handler404 = error_404_view
