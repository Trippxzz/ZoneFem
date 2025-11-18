from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse, Http404
from .forms import UsuarioForm, EmailAuthenticationForm, ServicioForm, ServicioImagenForm, seleccionarServicioForm, disponibilidadServicioFormSet, ContactoForm
from .models import BloqueServicio, Usuario, Servicio, ImagenServicio, disponibilidadServicio, Reservas, Carrito, CarritoItem, Matrona
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import calendar
# Create your views here.

def home(request):
    loginf = EmailAuthenticationForm()
    servicios = Servicio.objects.all().order_by('nombre')
    contacto_form = ContactoForm()
    context = {'loginf': loginf, 'servicios': servicios, 'contacto_form': contacto_form}
    return render(request, "index.html", context)

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
        return redirect('home')
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
        servicios = Servicio.objects.all()
        return render(request, 'ZoneServicios/servicios.html', {'servicios': servicios})
    
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



def contacto_view(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        
        # if form.is_valid():
        #     nombre = form.cleaned_data['nombre']
        #     email = form.cleaned_data['email']
        #     phone = form.cleaned_data['phone']
        #     mensaje = form.cleaned_data['message']

        #     asunto = f"Mensaje de Contacto ZONEFEM - {nombre}"
        #     cuerpo_mensaje = f"""
        #     Nombre: {nombre}
        #     Email: {email}
        #     Teléfono: {phone or 'No proporcionado'}

        #     --- Mensaje ---
        #     {mensaje}
        #     """

        #     # 2. Enviar el correo (¡Nota: Esto requiere configuración de EMAIL_BACKEND en settings.py!)
        #     try:
        #         # Simplemente lo imprime en la consola en modo DEBUG
        #         send_mail(
        #             asunto,
        #             cuerpo_mensaje,
        #             settings.DEFAULT_FROM_EMAIL, # Remitente (ej: 'no-reply@ZONEFEM.com')
        #             ['tu_email_destino@ejemplo.com'], # Destinatario (Tu correo real)
        #             fail_silently=False,
        #         )
                

        #         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        #             return JsonResponse({'success': True, 'message': 'Tu mensaje ha sido enviado con éxito.'})
                

        #         return redirect('home') 

        #     except Exception as e:
        #         # Si el envío del correo falla (ej: mala configuración de SMTP)
        #         print(f"Error al enviar correo: {e}")
        #         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        #             return JsonResponse({'success': False, 'errors': 'Error del servidor al enviar el correo.'}, status=500)
                
        #         form.add_error(None, 'Hubo un error al enviar tu mensaje. Intenta de nuevo más tarde.')

        # else:
        #     # Si la validación falla (para peticiones AJAX)
        #     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        #         return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # Si es una petición GET o si la validación falló en una petición normal
    form = ContactoForm() 
    return render(request, 'ZoneComponentes/contacto.html', {'form': form})

def generarHoras(dsemana: int, fecha: datetime.date, servicioid: int):
    disponibilidad = disponibilidadServicio.objects.filter(
        bloque_servicio__servicio__id=servicioid, 
        dia_semana=dsemana
    ).select_related('bloque_servicio__matrona') 
    
    if not disponibilidad.exists():
        return []
    
    duracion = disponibilidad.first().bloque_servicio.servicio.duracion 
    
    reservas_existentes = Reservas.objects.filter(
        servicio__id=servicioid, 
        fecha=fecha, 
        estado__in=['P', 'C']
    ).values('matrona_id', 'hora_inicio')
    
    slots_ocupados = set((r['matrona_id'], r['hora_inicio'].strftime("%H:%M")) for r in reservas_existentes)
    horas_disponibles = []
    
    for dispo in disponibilidad:
        matrona_usuario = dispo.bloque_servicio.matrona
        matrona_id = matrona_usuario.id
        
        matrona_nombre = matrona_usuario.get_full_name() or matrona_usuario.email 
        
        start_time = datetime.combine(fecha, dispo.hora_inicio)
        end_time = datetime.combine(fecha, dispo.hora_fin)
        
        current_slot = start_time
        
        while current_slot + timedelta(minutes=duracion) <= end_time:
            slot_inicio_str = current_slot.strftime("%H:%M")
            slot_fin = current_slot + timedelta(minutes=duracion)
            
            if (matrona_id, slot_inicio_str) in slots_ocupados:
                current_slot += timedelta(minutes=duracion)
                continue
                
            horas_disponibles.append({
                'matrona_id': matrona_id,
                'matrona_nombre': matrona_nombre,
                'hora_inicio': slot_inicio_str,
                'hora_fin': slot_fin.strftime("%H:%M"),
                'fecha': fecha.isoformat(),
                'colorm': f"#{matrona_id * 100 % 0xFFFFFF:06x}" 
            })
            
            current_slot += timedelta(minutes=duracion)
            
    return horas_disponibles

def seleccionarHora(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    
    fecha_seleccionada_str = request.GET.get('fecha', datetime.now().strftime("%Y-%m-%d")) 
    
    try:
        fecha_seleccionada = datetime.strptime(fecha_seleccionada_str, "%Y-%m-%d").date()
        dia_semana_num = fecha_seleccionada.weekday()
    except ValueError:
        # Si la fecha es inválida, devuelve un error JSON
        return JsonResponse({'slots': [], 'error': 'Formato de fecha inválido'}, status=400)
        
    # Generar los slots
    slots = generarHoras(dia_semana_num, fecha_seleccionada, servicio_id)

    return JsonResponse({'slots': slots, 'fecha': fecha_seleccionada_str})

# views.py

@login_required
def reservarHora(request, servicio_id=None): 
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        servicio_id = request.POST.get('servicio_id', servicio_id) 
        if not servicio_id:
             raise ValueError("ID de servicio no proporcionado.")
             
        matrona_id = request.POST.get('matrona_id')
        fecha_reserva_str = request.POST.get('fecha')
        hora_inicio_str = request.POST.get('hora_inicio')
        
        servicio = get_object_or_404(Servicio, id=servicio_id)
        matrona = get_object_or_404(Usuario, id=matrona_id, rol='matrona') 
        cliente = request.user
        
        duracion = servicio.duracion 
        
        dt_inicio = datetime.strptime(f"{fecha_reserva_str} {hora_inicio_str}", "%Y-%m-%d %H:%M")
        dt_fin = dt_inicio + timedelta(minutes=duracion)
        
    except (ValueError, Http404) as e:
        return JsonResponse({'success': False, 'error': f'Datos de reserva inválidos: {e}'}, status=400)
    
    if Reservas.objects.filter(
        matrona=matrona, 
        fecha=dt_inicio.date(), 
        hora_inicio=dt_inicio.time(),
        estado__in=['P','C']).exists():
        return JsonResponse({'success': False, 'error': 'La hora seleccionada ya no está disponible'}, status=409)
    

    with transaction.atomic():
        reserva = Reservas.objects.create(

            usuario=cliente, 
            servicio=servicio,
            matrona=matrona,
            fecha=dt_inicio.date(),
            hora_inicio=dt_inicio.time(),
            hora_fin=dt_fin.time(),
            estado='P' 
        )
        carrito, _ = Carrito.objects.get_or_create(usuario=cliente) 
        
        item = CarritoItem.objects.create(
            carrito=carrito,
            servicio=servicio,
            cantidad=1
        )
        
        reserva.carrito_item = item
        reserva.save()
        
    return JsonResponse({'success': True, 'redirect_url': reverse('ver_carrito')})

@login_required
def verCarrito(request):
    try:
        carrito = Carrito.objects.get(usuario=request.user)
    except Carrito.DoesNotExist:
        carrito = Carrito.objects.create(usuario=request.user)
    
    items = CarritoItem.objects.filter(carrito=carrito).select_related(
        'reserva_asociada', 
        'servicio',
        'reserva_asociada__matrona__usuario'). prefetch_related('reserva_asociada__matrona')
    
    context = {'carrito': carrito, 'items': items, 'total': carrito.total}
    return render(request, 'ZoneServicios/carrito.html', context)

@login_required
def eliminarItemCarrito(request, item_id):
    try:
        carrito = Carrito.objects.get(usuario=request.user)
    except Carrito.DoesNotExist:
        raise Http404("Carrito no encontrado")
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    with transaction.atomic():
        try:
            reserva = item.reserva_asociada
            reserva.estado = 'X'  # Cancelada/Expirada
            reserva.carrito_item = None
            reserva.save()
        except Reservas.DoesNotExist:
            pass
        item.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'item_id': item_id, 'total': carrito.total})
    return redirect(reverse('vercarrito'))


@login_required
def panelServicio(request):
    if request.user.rol != 'matrona':
        return redirect('home')
    if request.method == 'POST':
        form = seleccionarServicioForm(matrona=request.user, data=request.POST)
        if form.is_valid():
            bloque_id = form.cleaned_data['bloque_servicio'].id
            return redirect('editar_disponibilidad_servicio', bloque_id=bloque_id)
    else:
        form = seleccionarServicioForm(matrona=request.user)
    return render(request, 'ZoneMatronas/panelservicio.html', {'form': form})

@login_required
def editardispoServicio(request, bloque_id):
    if request.user.rol != 'matrona':
        return redirect('home')

    bloque = get_object_or_404(BloqueServicio, id=bloque_id, matrona=request.user)
    if request.method == 'POST':
        formset = disponibilidadServicioFormSet(request.POST, request.FILES, instance=bloque)
        if formset.is_valid():
            with transaction.atomic():
                formset.save()
            return redirect('panel_matrona_servicios')
    else:
        formset = disponibilidadServicioFormSet(instance=bloque)
    context = {'formset': formset, 'bloque': bloque}
    return render(request, 'ZoneMatronas/editardisponibilidad.html', context)
       