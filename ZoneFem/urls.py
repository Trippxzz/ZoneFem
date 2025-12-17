from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from ZoneApp import views
urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', views.home, name='home'),
    path('registro/', views.RegistroUsuarios, name='registro'),
    path('login_ajax/', views.login_ajax, name='login_ajax'), 
    path('miperfil/', views.perfil_usuario, name='miperfil'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('crear_servicio/', views.crearServicio, name='crearservicio'),
    path('contacto/', views.contacto_view, name='contacto'),
    path('servicios/', views.verServicio, name='verservicio'),
    path('servicio/<int:id>/', views.detServicio, name='detalleservicio'),
    path('servicio/<int:servicio_id>/opinion/', views.crear_opinion_servicio, name='crear_opinion_servicio'),
    path('editar_servicio/<int:id>/', views.editServicio, name='editarservicio'),
    path('servicios/<int:servicio_id>/toggle/', views.toggle_servicio, name='toggle_servicio'),
    path('eliminar_servicio/<int:id>/', views.eliminarServicio, name='eliminarservicio'),
    path('eliminar_imagen/<int:id>/', views.eliminarImagen, name='eliminarimagenservicio'),
    path('cambiar_principal/<int:imagen_id>/', views.cambiar_principal, name='cambiar_principal'),
    path('carrito/', views.verCarrito, name='ver_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminarItemCarrito, name='eliminaritemcarrito'),
    path('carrito/aplicar_cupon/', views.aplicar_cupon, name='aplicar_cupon'),
    path('carrito/quitar_cupon/', views.quitar_cupon, name='quitar_cupon'),
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
    path('panelmatrona', views.panel_matrona, name = 'panel_matrona'),
    path('matrona/pacientes/', views.lista_pacientes_matrona, name='lista_pacientes_matrona'),
    path('matrona/ficha/crear/', views.crear_ficha_clinica, name='crear_ficha_clinica'),
    path('matrona/ficha/<int:paciente_id>/', views.ver_ficha_clinica, name='ver_ficha_clinica'),
    path('matrona/ficha/<int:paciente_id>/editar/', views.editar_ficha_clinica, name='editar_ficha_clinica'),
    path('matrona/paciente/<int:paciente_id>/', views.detalle_paciente, name='detallePaciente'),
    path('matrona/paciente/<int:paciente_id>/historial/', views.historial_paciente, name='historial_paciente'),
    path('matrona/<int:matrona_id>/info/', views.info_matrona, name='info_matrona'),
    path('panelmatrona/perfil/', views.perfil_matrona, name='perfil_matrona'),
    #  Administración 
    path('gestion/asignar_servicios/', views.admin_asignar_servicios, name='admin_asignar_servicios'),
    path('gestion/lista_servicios/', views.admin_lista_servicios, name='admin_lista_servicios'),
    path('gestion/usuarios/', views.admin_gestionar_usuarios, name='admin_gestionar_usuarios'),
    path('gestion/usuarios/<int:usuario_id>/cambiar_rol/', views.admin_cambiar_rol_usuario, name='admin_cambiar_rol_usuario'),
    path('gestion/cupones/', views.admin_cupones, name='admin_cupones'),
    path('gestion/cupones/crear/', views.admin_crear_cupon, name='admin_crear_cupon'),
    path('gestion/cupones/editar/<int:cupon_id>/', views.admin_editar_cupon, name='admin_editar_cupon'),
    path('gestion/cupones/eliminar/<int:cupon_id>/', views.admin_eliminar_cupon, name='admin_eliminar_cupon'),
    path('gestion/cupones/toggle/<int:cupon_id>/', views.admin_toggle_cupon, name='admin_toggle_cupon'),
    path('gestion/anuncios/', views.admin_anuncios, name='admin_anuncios'),
    path('gestion/anuncios/crear/', views.admin_crear_anuncio, name='admin_crear_anuncio'),
    path('gestion/anuncios/editar/<int:anuncio_id>/', views.admin_editar_anuncio, name='admin_editar_anuncio'),
    path('gestion/anuncios/eliminar/<int:anuncio_id>/', views.admin_eliminar_anuncio, name='admin_eliminar_anuncio'),
    path('gestion/anuncios/toggle/<int:anuncio_id>/', views.admin_toggle_anuncio, name='admin_toggle_anuncio'),
    # Ruleta
    path('gestion/ruleta/', views.admin_ruleta, name='admin_ruleta'),
    path('gestion/ruleta/crear/', views.admin_crear_beneficio_ruleta, name='admin_crear_beneficio_ruleta'),
    path('gestion/ruleta/editar/<int:beneficio_id>/', views.admin_editar_beneficio_ruleta, name='admin_editar_beneficio_ruleta'),
    path('gestion/ruleta/eliminar/<int:beneficio_id>/', views.admin_eliminar_beneficio_ruleta, name='admin_eliminar_beneficio_ruleta'),
    path('gestion/ruleta/toggle/<int:beneficio_id>/', views.admin_toggle_beneficio_ruleta, name='admin_toggle_beneficio_ruleta'),
    path('ruleta/verificar/', views.verificar_ruleta, name='verificar_ruleta'),
    path('ruleta/girar/', views.girar_ruleta, name='girar_ruleta'),
    # Panel Usuario
    path('mi-panel/', views.panel_usuario, name='panel_usuario'),
    # Cursos
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('cursos/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('cursos/<int:curso_id>/inscribir/', views.inscribir_curso, name='inscribir_curso'),
    path('mis-cursos/', views.mis_cursos, name='mis_cursos'),
    # Matrona - Cursos
    path('matrona/cursos/', views.cursos_matrona, name='cursos_matrona'),
    path('matrona/cursos/crear/', views.crear_curso, name='crear_curso'),
    path('matrona/cursos/<int:curso_id>/editar/', views.editar_curso, name='editar_curso'),
    path('matrona/cursos/<int:curso_id>/toggle/', views.toggle_curso, name='toggle_curso'),
    path('matrona/cursos/<int:curso_id>/eliminar/', views.eliminar_curso, name='eliminar_curso'),
    path('matrona/cursos/<int:curso_id>/inscritos/', views.inscritos_curso, name='inscritos_curso'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    