from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from ZoneApp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('registro/', views.RegistroUsuarios, name='registro'),
    path('login_ajax/', views.login_ajax, name='login_ajax'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('crear_servicio/', views.crearServicio, name='crearservicio'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('servicios/', views.verServicio, name='verservicio'),
    path('servicio/<int:id>/', views.detServicio, name='detalleservicio'),
    path('editar_servicio/<int:id>/', views.editServicio, name='editarservicio'),
    path('eliminar_servicio/<int:id>/', views.eliminarServicio, name='eliminarservicio'),
    path('eliminar_imagen/<int:id>/', views.eliminarImagen, name='eliminarimagenservicio'),
    path('cambiar_principal/<int:imagen_id>/', views.cambiar_principal, name='cambiar_principal'),
    path('carrito/', views.verCarrito, name='ver_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminarItemCarrito, name='eliminaritemcarrito'),
    path('panel/', views.panelServicio, name='panel_matrona_servicios'),
    path('disponibilidad/editar/<int:bloque_id>/', views.editardispoServicio, name='editar_disponibilidad_servicio'),
    path('seleccionar_hora/<int:servicio_id>/', views.seleccionarHora, name='seleccionar_hora'),
    path('reservar_hora/', views.reservarHora, name='reservar_hora'),
    # URLs de Webpay
    path('pago/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('pago/resultado/<str:resultado>/', views.resultado_pago, name='resultado_pago'),
    path('pago/resultado/<str:resultado>/<int:venta_id>/', views.resultado_pago, name='resultado_pago'),
    ##RECUPERAR CONTRASEÑA
 path('recuperar_contrasena/', views.recuperar_contra, name='recuperar_contra'),
    path('reset_contrasena/<uidb64>/<token>/', views.restablecer_contra, name='restablecer_contra'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    