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
    path('servicios/', views.verServicio, name='verservicio'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)