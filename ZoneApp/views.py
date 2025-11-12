from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import UsuarioForm, EmailAuthenticationForm, ServicioForm, ServicioImagenForm
from .models import Usuario, Servicio, ImagenServicio
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.

def home(request):
    loginf = EmailAuthenticationForm()
    return render(request, "index.html", {'loginf': loginf})

### ZONE REGISTRO E INICIO DE SESIÓN 
def RegistroUsuarios(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password')
            user_auth = authenticate(request, email=user.email, password=raw_password)
            if user_auth is not None:
                login(request, user_auth)  # Inicia sesión automáticamente después del registro
            return redirect('home')
    else:
        form = UsuarioForm()
    return render(request, 'ZoneUsuarios/registrousers.html', {'form': form})

@require_POST       
def login_ajax(request):
    form = EmailAuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return JsonResponse({'success': True, 'redirect_url': reverse_lazy('home')})
    return JsonResponse({'success': False, 'errors': form.errors})

####Sección CRUD Servicios

def crearServicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        formimg = ServicioImagenForm(request.POST, request.FILES or None)
        if form.is_valid():
            servicio = form.save()
            img_list = request.FILES.getlist('imagenes')
            imgprincipal = int(request.POST.get('imgprincipal',0))
            for i, imgfile in enumerate(img_list):
                ImagenServicio.objects.create(servicio=servicio, imagen=imgfile, es_principal=(i==imgprincipal))
            return redirect('verservicio')
        else:
            print("error prod:",form.errors)
            print("error img:",formimg.errors)
            return redirect('home')
    else:
        form = ServicioForm()
        formimg = ServicioImagenForm()
    return render(request, 'ZoneCreacion/crearserv.html', {'form': form, 'formimg': formimg})

def verServicio(request):
    if request.method == 'GET':
        servicio = Servicio.objects.all()
        return render(request, 'ZoneServicios/servicios.html', {'servicio': servicio})
    
def detServicio(request, id):
    if request.method == 'GET':
        serv = Servicio.objects.get(id = id)
        imgserv = serv.imagenes.all()
        return render (request, "servicio.html", {"serv":serv, "imgs":imgserv})



