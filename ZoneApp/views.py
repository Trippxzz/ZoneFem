from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
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
        return render (request, "ZoneServicios/servicio.html", {"serv":serv, "imgs":imgserv})


def editServicio(request, id):
    serv = get_object_or_404(Servicio, id=id)
    imgs = serv.imagenes.all()
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=serv)
        formimg = ServicioImagenForm(request.POST, request.FILES or None)
        if form.is_valid():
            servicio = form.save()
            # Guarda las imágenes nuevas que se suban (si las hay)
            img_list = request.FILES.getlist('imagenes')
            for img in img_list:
                ImagenServicio.objects.create(servicio=servicio, imagen=img, es_principal=False)
            # Responder según tipo de petición: AJAX -> JSON, normal -> redirect
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('editarservicio', args=[servicio.id])})
            return redirect(reverse('editarservicio', args=[servicio.id]))
        else:
            # Si es AJAX, devolver errores en JSON para que el frontend los muestre
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            return render(request, 'ZoneEdicion/editserv.html', {'form': form, 'formimg': formimg, 'serv': serv, 'imgs': imgs})
    else:
        form = ServicioForm(instance=serv)
        return render(request, 'ZoneEdicion/editserv.html', {'form': form, 'serv': serv, 'imgs': imgs})


def eliminarServicio(request, id):
    serv = get_object_or_404(Servicio, id=id)
    if request.method == "POST":
        serv.delete()
        return redirect("home")
    
def cambiar_principal(request, imagen_id):
    imagen = get_object_or_404(ImagenServicio, id=imagen_id)
    servicio = imagen.servicio
    if request.method == "POST":
        # Desmarcar todas las imágenes como principal
        ImagenServicio.objects.filter(servicio=servicio).update(es_principal=False)
        # Marcar la seleccionada como principal
        imagen.es_principal = True
        imagen.save()
        return redirect(reverse('editarservicio', args=[servicio.id]))
    return HttpResponse("Método no permitido", status=405)

def eliminarImagen(request, imagen_id=None, id=None):
    actual_id = imagen_id if imagen_id is not None else id
    if actual_id is None:
        return HttpResponse("Imagen no especificada", status=400)
    imagen = get_object_or_404(ImagenServicio, id=actual_id)
    servicio_id = imagen.servicio.id
    if request.method == "POST":
        imagen.delete()
        return redirect(reverse('editarservicio', args=[servicio_id]))
    return HttpResponse("Método no permitido", status=405)

