from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse, Http404
from .forms import UsuarioForm, EmailAuthenticationForm, ServicioForm, ServicioImagenForm, seleccionarServicioForm, disponibilidadServicioFormSet, ContactoForm, PerfilMatronaForm, EditarPerfilUsuarioForm
from .models import BloqueServicio, Usuario, Servicio, ImagenServicio, disponibilidadServicio, Reservas, Carrito, CarritoItem, Matrona, Venta, Pagos, FichaClinica, Cupon, UsoCupon, Curso, ImagenCurso, InscripcionCurso, OpinionServicio, Anuncio, RuletaBeneficio, UsuarioRuleta
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import calendar
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
# Create your views here.

def home(request):
    from django.utils import timezone
    loginf = EmailAuthenticationForm()
    servicios = Servicio.objects.filter(activo=True).order_by('nombre')
    contacto_form = ContactoForm()
    matronas = Matrona.objects.select_related('usuario').all()
    
    # Obtener anuncios activos y vigentes
    anuncios = Anuncio.objects.filter(activo=True)
    anuncios_vigentes = [a for a in anuncios if a.esta_vigente()]
    
    context = {
        'loginf': loginf, 
        'servicios': servicios, 
        'contacto_form': contacto_form, 
        'matronas': matronas,
        'anuncios': anuncios_vigentes
    }
    return render(request, "index.html", context)

### ZONE REGISTRO E INICIO DE SESIÓN 
def RegistroUsuarios(request):
    """Maneja el registro desde el modal - solo POST"""
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
            # Si hay errores, devolver JSON con los errores y datos para mantener el formulario
            from django.http import JsonResponse
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]
            
            return JsonResponse({
                'success': False,
                'errors': errors,
                'data': {
                    'first_name': request.POST.get('first_name', ''),
                    'email': request.POST.get('email', ''),
                    'rut': request.POST.get('rut', ''),
                    'telefono': request.POST.get('telefono', ''),
                    'fecha_nacimiento': request.POST.get('fecha_nacimiento', ''),
                }
            })
    else:
        # Si acceden por GET, redirigir a home
        return redirect('home')

@ratelimit(key='ip', rate='5/m', method='POST') ###METODO DE SEGUIRDAD 
def login_ajax(request):
    form = EmailAuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('home')
    else:
        print("error en login")
        # messages.error(request, 'Credenciales inválidas. Por favor, verifica tu email y contraseña.')
        return redirect('home')

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
        servicios = Servicio.objects.filter(activo=True)
        return render(request, 'ZoneServicios/servicios.html', {'servicios': servicios})
    
def detServicio(request, id):
    if request.method == 'GET':
        serv = Servicio.objects.get(id=id)
        imgserv = serv.imagenes.all()
        opiniones = serv.opiniones.all()
        
        # Verificar si el usuario puede opinar (ha comprado el servicio y no ha opinado)
        puede_opinar = False
        ya_opino = False
        if request.user.is_authenticated:
            # Verificar si ha comprado el servicio (reserva confirmada/pagada)
            ha_comprado = Reservas.objects.filter(
                usuario=request.user, 
                servicio=serv, 
                estado='C'
            ).exists()
            
            # Verificar si ya opinó
            ya_opino = OpinionServicio.objects.filter(
                usuario=request.user,
                servicio=serv
            ).exists()
            
            puede_opinar = ha_comprado and not ya_opino
        
        context = {
            'serv': serv,
            'imgs': imgserv,
            'opiniones': opiniones,
            'puede_opinar': puede_opinar,
            'ya_opino': ya_opino,
        }
        return render(request, "ZoneServicios/servicio.html", context)


@login_required
def crear_opinion_servicio(request, servicio_id):
    """Vista para crear una opinión de servicio"""
    if request.method == 'POST':
        servicio = get_object_or_404(Servicio, id=servicio_id)
        
        # Verificar que el usuario haya comprado el servicio
        ha_comprado = Reservas.objects.filter(
            usuario=request.user,
            servicio=servicio,
            estado='C'
        ).exists()
        
        if not ha_comprado:
            return JsonResponse({
                'success': False,
                'message': 'Solo puedes opinar sobre servicios que hayas contratado'
            })
        
        # Verificar que no haya opinado antes
        if OpinionServicio.objects.filter(usuario=request.user, servicio=servicio).exists():
            return JsonResponse({
                'success': False,
                'message': 'Ya has opinado sobre este servicio'
            })
        
        # Crear la opinión
        calificacion = request.POST.get('calificacion')
        comentario = request.POST.get('comentario', '').strip()
        
        if not calificacion or not comentario:
            return JsonResponse({
                'success': False,
                'message': 'Debes proporcionar una calificación y comentario'
            })
        
        OpinionServicio.objects.create(
            servicio=servicio,
            usuario=request.user,
            calificacion=int(calificacion),
            comentario=comentario
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Opinión guardada exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


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

### DESACTIVADO POR EL MOMENTO POR MEDIDAS DE SEGURIDAD
@login_required
def eliminarServicio(request, id):
    """Vista para eliminar permanentemente un servicio"""
    if request.user.rol != 'matrona' and not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'No tienes permisos'})
    
    if request.method == "POST":
        serv = get_object_or_404(Servicio, id=id)
        
        # Verificar si tiene reservas confirmadas o pendientes
        if Venta.objects.filter(servicio=serv, estado__in=['C', 'P']).exists():
            return JsonResponse({
                'success': False, 
                'message': 'No puedes eliminar un servicio con reservas activas. Usa la opción de ocultar.'
            })
        
        nombre = serv.nombre
        serv.delete()
        return JsonResponse({
            'success': True,
            'message': f'Servicio "{nombre}" eliminado exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

###SECCION PARA ESTABLECER SI SE MUESTRA O NO EL SERVICIO / PREVENCION DE SEGURIDAD ANTE ELIMINACIÓN DE UN SERVICIO
@login_required
def toggle_servicio(request, servicio_id):
    if request.user.rol != 'matrona' and not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'No tienes permisos'})
    
    if request.method == 'POST':
        serv = get_object_or_404(Servicio, id=servicio_id)
        serv.activo = not serv.activo
        serv.save()
        
        estado = 'visible' if serv.activo else 'oculto'
        return JsonResponse({
            'success': True, 
            'message': f'Servicio "{serv.nombre}" ahora está {estado}',
            'activo': serv.activo
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

###IMAGEN PRINCIPAL
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
        try:
            color_matrona = matrona_usuario.perfil_matrona.color_agenda
        except:
            color_matrona = '#7436ad'
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
                'colorm': color_matrona
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
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    items = CarritoItem.objects.filter(carrito=carrito).select_related(
        'servicio', 'curso'
    ).prefetch_related('servicio__imagenes', 'curso__imagenes_curso')
    
    # Agregar información de reservas si existen (para servicios)
    for item in items:
        if item.servicio:
            try:
                item.reserva_asociada = Reservas.objects.get(carrito_item=item)
            except Reservas.DoesNotExist:
                item.reserva_asociada = None
        else:
            item.reserva_asociada = None
    
    context = {'carrito': carrito, 'items': items}
    return render(request, 'ZoneServicios/carrito.html', context)

@login_required
def eliminarItemCarrito(request, item_id):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    
    with transaction.atomic():
        # Si es un servicio, cancelar la reserva
        if item.servicio:
            try:
                reserva = Reservas.objects.get(carrito_item=item)
                reserva.estado = 'X'  # Cancelada/Expirada
                reserva.carrito_item = None
                reserva.save()
            except Reservas.DoesNotExist:
                pass
        
        # Si es un curso, eliminar la inscripción pendiente
        elif item.curso:
            InscripcionCurso.objects.filter(
                curso=item.curso,
                usuario=request.user,
                estado='pendiente'
            ).delete()
        
        item.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'item_id': item_id, 'total': carrito.total})
    return redirect('ver_carrito')


@login_required
def aplicar_cupon(request):
    """Vista para aplicar un cupón al carrito"""
    if request.method == 'POST':
        codigo_cupon = request.POST.get('codigo_cupon', '').strip().upper()
        
        if not codigo_cupon:
            return JsonResponse({'success': False, 'error': 'Por favor ingresa un código de cupón'})
        
        try:
            cupon = Cupon.objects.get(codigo=codigo_cupon)
        except Cupon.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El cupón no existe'})
        
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        # Validar el cupón
        valido, mensaje = cupon.es_valido(request.user, float(carrito.subtotal))
        
        if not valido:
            return JsonResponse({'success': False, 'error': mensaje})
        
        # Aplicar cupón
        carrito.cupon_aplicado = cupon
        carrito.save()
        
        descuento = float(carrito.descuento)
        total = float(carrito.total)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Cupón {cupon.codigo} aplicado correctamente',
            'descuento': descuento,
            'total': total,
            'codigo_cupon': cupon.codigo
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def quitar_cupon(request):
    """Vista para quitar el cupón del carrito"""
    if request.method == 'POST':
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        carrito.cupon_aplicado = None
        carrito.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Cupón eliminado',
            'total': float(carrito.total)
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def panelServicio(request):
    if request.user.rol != 'matrona':
        return redirect('home')
    
    # Obtener bloques directamente
    bloques = BloqueServicio.objects.filter(matrona=request.user).select_related('servicio')
    
    if request.method == 'POST':
        form = seleccionarServicioForm(matrona=request.user, data=request.POST)
        if form.is_valid():
            bloque_id = form.cleaned_data['bloque_servicio'].id
            return redirect('editar_disponibilidad_servicio', bloque_id=bloque_id)
    else:
        form = seleccionarServicioForm(matrona=request.user)
    
    return render(request, 'ZoneMatronas/panelservicio.html', {
        'form': form,
        'bloques': bloques
    })

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


###  SECCIÓN WEBPAY

@login_required
def iniciar_pago(request):
    try:
        # Obtener el carrito del usuario
        carrito = Carrito.objects.get(usuario=request.user)
        items = CarritoItem.objects.filter(carrito=carrito)
        
        if not items.exists():
            return redirect('ver_carrito')
        
        # Calcular el total
        total = int(carrito.total)
        
        if total <= 0:
            return redirect('ver_carrito')
        
        with transaction.atomic():
            # Crear la venta
            venta = Venta.objects.create(
                rut=request.user,
                total_venta=total,
                estado='PENDIENTE'
            )
            
            # Crear el pago asociado
            pago = Pagos.objects.create(
                venta=venta,
                monto_total=total,
                estado='PENDIENTE'
            )
            
            # Configurar Webpay
            if settings.WEBPAY_ENVIRONMENT == 'PRODUCCION':
                options = WebpayOptions(
                    commerce_code=settings.WEBPAY_COMMERCE_CODE,
                    api_key=settings.WEBPAY_API_KEY,
                    integration_type=IntegrationType.LIVE
                )
            else:
                # Usar credenciales de integración por defecto
                options = WebpayOptions(
                    commerce_code='597055555532',
                    api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
                    integration_type=IntegrationType.TEST
                )
            
            # Generar orden de compra única
            buy_order = f"ORDER-{venta.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            session_id = str(request.user.id)
            return_url = request.build_absolute_uri(reverse('confirmar_pago'))
            
            # Crear transacción en Webpay
            tx = Transaction(options)
            response = tx.create(buy_order, session_id, total, return_url)
            
            # Guardar el token en el pago
            pago.token_ws = response['token']
            pago.save()
            
            # Guardar información en sesión para validar después
            request.session['venta_id'] = venta.id
            request.session['buy_order'] = buy_order
            
            # Redirigir a Webpay
            return redirect(f"{response['url']}?token_ws={response['token']}")
            
    except Carrito.DoesNotExist:
        return redirect('ver_carrito')
    except Exception as e:
        print(f"Error al iniciar pago: {e}")
        return render(request, 'ZonePagos/error_pago.html', {
            'error': 'Ocurrió un error al procesar el pago. Por favor, intenta nuevamente.'
        })
 

@csrf_exempt
def confirmar_pago(request):
    """
    Callback de Webpay después del pago
    Valida la transacción y actualiza el estado
    """
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    
    if not token:
        print("No se recibió token")
        return redirect('resultado_pago', resultado='error')
    
    try:
        # Configurar opciones según el ambiente
        if settings.WEBPAY_ENVIRONMENT == 'PRODUCCION':
            options = WebpayOptions(
                commerce_code=settings.WEBPAY_COMMERCE_CODE,
                api_key=settings.WEBPAY_API_KEY,
                integration_type=IntegrationType.LIVE
            )
        else:
            options = WebpayOptions(
                commerce_code='597055555532',
                api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
                integration_type=IntegrationType.TEST
            )
        
        # Consultar el estado de la transacción en Webpay
        tx = Transaction(options)
        response = tx.commit(token)
        
        print(f"Respuesta de Webpay: {response}")
        
        # Buscar el pago por token
        pago = Pagos.objects.get(token_ws=token)
        venta = pago.venta
        
        if response.get('response_code') == 0:
            carrito = Carrito.objects.get(usuario=venta.rut)
            items = CarritoItem.objects.filter(carrito=carrito).select_related('servicio', 'curso')
            
            reservas_info = []
            cursos_info = []
            
            for item in items:
                if item.servicio:
                    try:
                        reserva = Reservas.objects.get(carrito_item=item)
                        reservas_info.append({
                            'servicio_nombre': reserva.servicio.nombre,
                            'servicio_precio': reserva.servicio.precio,
                            'fecha': reserva.fecha.strftime('%d/%m/%Y'),
                            'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
                            'hora_fin': reserva.hora_fin.strftime('%H:%M'),
                            'matrona': reserva.matrona.get_full_name(),
                        })
                    except Reservas.DoesNotExist:
                        pass
                elif item.curso:
                    cursos_info.append({
                        'curso_nombre': item.curso.nombre,
                        'curso_precio': item.curso.precio,
                        'fecha_inicio': item.curso.fecha_inicio.strftime('%d/%m/%Y'),
                        'fecha_termino': item.curso.fecha_termino.strftime('%d/%m/%Y'),
                        'duracion': item.curso.duracion_horas,
                        'matrona': item.curso.matrona.get_full_name(),
                        'link': item.curso.link_reunion or 'Se enviará próximamente'
                    })
            
            # Ahora actualizar la base de datos
            with transaction.atomic():
                pago.estado = 'APROBADO'
                pago.codigo_autorizacion = response.get('authorization_code', '')
                pago.tipo_pago = response.get('payment_type_code', '')
                pago.save()
                
                venta.estado = 'CONFIRMADA'
                venta.save()
                
                # Registrar uso de cupón si existe
                if carrito.cupon_aplicado:
                    UsoCupon.objects.create(
                        cupon=carrito.cupon_aplicado,
                        usuario=venta.rut,
                        venta=venta,
                        monto_descuento=carrito.descuento
                    )
                    # Incrementar usos del cupón
                    carrito.cupon_aplicado.usos_actuales += 1
                    carrito.cupon_aplicado.save()
                
                for item in items:
                    if item.servicio:
                        try:
                            reserva = Reservas.objects.get(carrito_item=item)
                            reserva.estado = 'C'
                            reserva.save()
                        except Reservas.DoesNotExist:
                            pass
                    elif item.curso:
                        # Crear o actualizar inscripción al curso
                        InscripcionCurso.objects.update_or_create(
                            curso=item.curso,
                            usuario=venta.rut,
                            defaults={'estado': 'confirmada'}
                        )
                
                items.delete()
                # Limpiar cupón del carrito
                carrito.cupon_aplicado = None
                carrito.save()
            
            # Preparar y enviar correo
            usuario = venta.rut
            nombre_completo = usuario.get_full_name() or usuario.email
            
            detalles_servicios = ""
            if reservas_info:
                detalles_servicios += "📅 SERVICIOS RESERVADOS:\n"
                detalles_servicios += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                for info in reservas_info:
                    detalles_servicios += f"• {info['servicio_nombre']}\n"
                    detalles_servicios += f"  Fecha: {info['fecha']}\n"
                    detalles_servicios += f"  Hora: {info['hora_inicio']} - {info['hora_fin']}\n"
                    detalles_servicios += f"  Matrona: {info['matrona']}\n\n"
            
            if cursos_info:
                if detalles_servicios:
                    detalles_servicios += "\n"
                detalles_servicios += "🎓 CURSOS INSCRITOS:\n"
                detalles_servicios += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                for info in cursos_info:
                    detalles_servicios += f"• {info['curso_nombre']}\n"
                    detalles_servicios += f"  Inicio: {info['fecha_inicio']}\n"
                    detalles_servicios += f"  Término: {info['fecha_termino']}\n"
                    detalles_servicios += f"  Duración: {info['duracion']} horas\n"
                    detalles_servicios += f"  Matrona: {info['matrona']}\n"
                    detalles_servicios += f"  Link: {info['link']}\n\n"
            
            if not detalles_servicios:
                detalles_servicios = "No se encontraron detalles"
            
            subject = '✅ Compra Confirmada - ZoneFem'
            message = f'''
Hola {nombre_completo},

¡Tu pago ha sido procesado exitosamente!

📋 DETALLES DE TU COMPRA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• ID de Venta: {venta.id}
• Total Pagado: ${venta.total_venta:,} CLP
• Fecha de Pago: {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}

{detalles_servicios}
‼️¡IMPORTANTE! 
• Para servicios: La matrona se contactará contigo para enviarte el link de la reunión en las próximas horas.
• Para cursos:Recibirás más información sobre el acceso antes de la fecha de inicio.

🤞Recuerda estar en un lugar sin ruido, para que nuestra comunicación sea óptima😊.

¿Necesitas reagendar o tienes dudas?
Contáctanos: contacto@zonefem.cl

Gracias por confiar en ZoneFem 💗

—
Equipo ZoneFem
            '''.strip()
            
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [usuario.email]
            
            try:
                send_mail(subject, message, from_email, to_email, fail_silently=False)
            except Exception as e:
                print(f"Error al enviar correo: {e}")
            
            return redirect('resultado_pago', resultado='exito', venta_id=venta.id)
        else:
            pago.estado = 'RECHAZADO'
            pago.save()
            venta.estado = 'ANULADA'
            venta.save()
            return redirect('resultado_pago', resultado='rechazado')
            
    except Pagos.DoesNotExist:
        print(f"No se encontró pago con token: {token}")
        return redirect('resultado_pago', resultado='error')
    except Exception as e:
        print(f"Error al confirmar pago: {e}")
        import traceback
        traceback.print_exc()
        return redirect('resultado_pago', resultado='error')


@login_required
def resultado_pago(request, resultado, venta_id=None):
    context = {'resultado': resultado}
    
    if resultado == 'exito' and venta_id:
        try:
            venta = Venta.objects.get(id=venta_id, rut=request.user)
            pago = Pagos.objects.get(venta=venta)
            context['venta'] = venta
            context['pago'] = pago
        except (Venta.DoesNotExist, Pagos.DoesNotExist):
            pass
    
    return render(request, 'ZonePagos/resultado_pago.html', context)

def recuperar_contra(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            usuario = Usuario.objects.get(email=email)
            
            # Generar token
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            
            # Crear URL de recuperación
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            reset_url = f"{protocol}://{current_site.domain}/reset_contrasena/{uid}/{token}/"
            
            # Enviar correo
            subject = 'Recuperación de Contraseña - ZoneFem'
            message = render_to_string('ZoneComponentes/reiniciar_contra-mail.html', {
                'usuario': usuario,
                'reset_url': reset_url,
                'domain': current_site.domain,
            })
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=message
                )
                messages.success(request, 'Te hemos enviado un correo con instrucciones para restablecer tu contraseña.')
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                messages.error(request, 'Error al enviar el correo. Verifica la configuración de email.')
            
            return redirect('home')
            
        except Usuario.DoesNotExist:
            # Por seguridad, mostramos el mismo mensaje aunque el usuario no exista
            # messages.success(request, 'Si el correo existe, te hemos enviado instrucciones para restablecer tu contraseña.')
            return redirect('home')
    
    return render(request, 'ZoneUsuarios/recuperar_contra.html')

def restablecer_contra(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    
    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password != password_confirm:
                # messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'ZoneUsuarios/restablecer_contra.html', {'validlink': True})
            
            if len(password) < 8:
                # messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                return render(request, 'ZoneUsuarios/restablecer_contra.html', {'validlink': True})
            
            # Cambiar contraseña
            usuario.set_password(password)
            usuario.save()
            
            # messages.success(request, '¡Contraseña cambiada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('home')
        
        return render(request, 'ZoneUsuarios/restablecer_contra.html', {'validlink': True})
    else:
        # messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return render(request, 'ZoneUsuarios/restablecer_contra.html', {'validlink': False})


@login_required
def panel_matrona(request):
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    reservas_hoy = Reservas.objects.filter(
        matrona=request.user,
        fecha=datetime.now().date(),
        estado='C'
    ).count()
    
    reservas_mes = Reservas.objects.filter(
        matrona=request.user,
        fecha__month=datetime.now().month,
        estado='C'
    ).count()
    
    total_pacientes = Reservas.objects.filter(
        matrona=request.user,
        estado='C'
    ).values('usuario').distinct().count()
    
    proximas_reservas = Reservas.objects.filter(
        matrona=request.user,
        estado='C',
        fecha__gte=datetime.now().date()
    ).select_related('usuario', 'servicio').order_by('fecha', 'hora_inicio')[:5] ## Para que solo sean 5 que se muestran en el resumen
    
    todas_reservas = Reservas.objects.filter(
        matrona=request.user,
        estado='C',
        fecha__gte=datetime.now().date()
    ).select_related('usuario', 'servicio').order_by('fecha', 'hora_inicio')
    
    context = {
        'reservas_hoy': reservas_hoy,
        'reservas_mes': reservas_mes,
        'total_pacientes': total_pacientes,
        'proximas_reservas': proximas_reservas,  # Solo 5
        'todas_reservas': todas_reservas,         # Todas para el modal
    }
    
    return render(request, 'ZoneMatronas/panelmatronas.html', context)

@login_required
def lista_pacientes(request):
    if request.user.rol != 'matrona':
        return redirect('home')
    
    pacientes_id = Reservas.objects.filter(
        matrona = request.user,
        estado = 'C'
    ).values_list('usuario__id', flat=True).distinct()
    pacientes = Usuario.objects.filter(id__in = pacientes_id)
    context = {'pacientes':pacientes}
    return render(request, 'ZoneMatronas/listaPacientes.html', context)

# @login_required
# def detalle_paciente(request, id):
#     if request.user.rol != 'matrona':
#         return redirect('home')
#     paciente = get_object_or_404(Usuario, id=id)
    
    
### IDEA PARA PERFIL DE USUARIO/VISTA DESDE MATRONA

##TABLA DE USUARIOS CON BOTON DE VER PERFIL, AL ABRIR PERFIL, QUE SE PUEDA MODIFICAR DATOS Y AGREGAR (FICHA CLINICA)
# TABLA CON RECETAS DADAS ¿?
# Ficha CLINICA UN CAMPO DE MUCHO TEXTO O VARIAS FICHAS SEGUN CITAS HAYAN (ESTILO POSIT)

@login_required
def perfil_usuario(request):  
    perfil_usuario = request.user
    if request.method == 'POST':
        form = EditarPerfilUsuarioForm(request.POST, instance=perfil_usuario)
        
        if form.is_valid():
            form.save()
            # messages.success(request, 'Perfil actualizado correctamente')
            return redirect('miperfil')
        else:
            messages.error(request, 'Error al actualizar el perfil')
    else:
        form = EditarPerfilUsuarioForm(instance=perfil_usuario)
    
    context = {
        'form': form,
        'perfil_usuario': perfil_usuario
    }
    
    return render(request, 'ZoneUsuarios/perfilusuario.html', context)


@login_required
def perfil_matrona(request):
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')

    try:
        perfil_matrona = request.user.perfil_matrona
    except ObjectDoesNotExist:
        perfil_matrona = Matrona.objects.create(
            usuario=request.user,
            color_agenda='#7436ad' # Valor por defecto
        )
    # -------------------

    if request.method == 'POST':
        form = PerfilMatronaForm(request.POST, request.FILES, instance=perfil_matrona)
        
        if form.is_valid():
            form.save()
            # Poner Notificacion
            return redirect('perfil_matrona')
        # else:
            # Poner Notificacion
    else:
        form = PerfilMatronaForm(instance=perfil_matrona)
    
    context = {
        'form': form,
        'perfil_matrona': perfil_matrona
    }
    
    return render(request, 'ZoneMatronas/perfilmatrona.html', context)



## ADMINISTRACIÓN

@login_required
def admin_asignar_servicios(request):
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_matrona')
    
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        matronas_ids = request.POST.getlist('matronas') 
        
        try:
            servicio = Servicio.objects.get(id=servicio_id)
            

            BloqueServicio.objects.filter(servicio=servicio).delete()
            
            for matrona_id in matronas_ids:
                matrona = Usuario.objects.get(id=matrona_id, rol='matrona')
                BloqueServicio.objects.create(
                    matrona=matrona,
                    servicio=servicio
                )
            
            # messages.success(request, f'Matronas asignadas correctamente al servicio {servicio.nombre}')
            return redirect('admin_asignar_servicios')
            
        except Exception as e:
            messages.error(request, f'Error al asignar matronas: {str(e)}')
    
    # Obtener todos los servicios y matronas
    servicios = Servicio.objects.all().order_by('nombre')
    matronas = Usuario.objects.filter(rol='matrona').order_by('first_name')
    
    # Obtener asignaciones actuales y agregarlas directamente al objeto servicio
    for servicio in servicios:
        servicio.matronas_asignadas = list(
            BloqueServicio.objects.filter(servicio=servicio).values_list('matrona_id', flat=True)
        )
    
    context = {
        'servicios': servicios,
        'matronas': matronas,
    }
    
    return render(request, 'ZoneAdmin/asignar_servicios.html', context)


@login_required
def admin_lista_servicios(request):
    """Vista para listar todos los servicios"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('panel_matrona')
    
    servicios = Servicio.objects.all().order_by('nombre')
    
    context = {
        'servicios': servicios,
    }
    
    return render(request, 'ZoneAdmin/lista_servicios.html', context)


@login_required
def admin_cupones(request):
    """Vista para administrar cupones"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    # Filtros
    estado_filtro = request.GET.get('estado', 'todos')
    busqueda = request.GET.get('busqueda', '')
    
    # Query base
    cupones = Cupon.objects.all()
    
    # Aplicar filtros
    if estado_filtro == 'activos':
        cupones = cupones.filter(activo=True, fecha_expiracion__gte=timezone.now())
    elif estado_filtro == 'expirados':
        cupones = cupones.filter(fecha_expiracion__lt=timezone.now())
    elif estado_filtro == 'inactivos':
        cupones = cupones.filter(activo=False)
    
    # Búsqueda
    if busqueda:
        cupones = cupones.filter(codigo__icontains=busqueda)
    
    cupones = cupones.order_by('-fecha_creacion')
    
    # Estadísticas
    total_cupones = Cupon.objects.count()
    cupones_activos = Cupon.objects.filter(activo=True, fecha_expiracion__gte=timezone.now()).count()
    cupones_expirados = Cupon.objects.filter(fecha_expiracion__lt=timezone.now()).count()
    total_usos = UsoCupon.objects.count()
    
    context = {
        'cupones': cupones,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
        'total_cupones': total_cupones,
        'cupones_activos': cupones_activos,
        'cupones_expirados': cupones_expirados,
        'total_usos': total_usos,
    }
    
    return render(request, 'ZoneAdmin/admin_cupones.html', context)


@login_required
def admin_crear_cupon(request):
    """Vista para crear un nuevo cupón"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            cupon = Cupon.objects.create(
                codigo=request.POST.get('codigo').upper(),
                descripcion=request.POST.get('descripcion', ''),
                tipo_descuento=request.POST.get('tipo_descuento'),
                valor_descuento=request.POST.get('valor_descuento'),
                monto_minimo=request.POST.get('monto_minimo') or None,
                usos_maximos=request.POST.get('usos_maximos') or None,
                usos_por_usuario=request.POST.get('usos_por_usuario', 1),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_expiracion=request.POST.get('fecha_expiracion'),
                activo=request.POST.get('activo') == 'on'
            )
            messages.success(request, f'Cupón {cupon.codigo} creado exitosamente')
            return redirect('admin_cupones')
        except Exception as e:
            messages.error(request, f'Error al crear cupón: {str(e)}')
    
    return render(request, 'ZoneAdmin/admin_crear_cupon.html')


@login_required
def admin_editar_cupon(request, cupon_id):
    """Vista para editar un cupón existente"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    cupon = get_object_or_404(Cupon, id=cupon_id)
    
    if request.method == 'POST':
        try:
            cupon.codigo = request.POST.get('codigo').upper()
            cupon.descripcion = request.POST.get('descripcion', '')
            cupon.tipo_descuento = request.POST.get('tipo_descuento')
            cupon.valor_descuento = request.POST.get('valor_descuento')
            cupon.monto_minimo = request.POST.get('monto_minimo') or None
            cupon.usos_maximos = request.POST.get('usos_maximos') or None
            cupon.usos_por_usuario = request.POST.get('usos_por_usuario', 1)
            cupon.fecha_inicio = request.POST.get('fecha_inicio')
            cupon.fecha_expiracion = request.POST.get('fecha_expiracion')
            cupon.activo = request.POST.get('activo') == 'on'
            cupon.save()
            
            messages.success(request, f'Cupón {cupon.codigo} actualizado exitosamente')
            return redirect('admin_cupones')
        except Exception as e:
            messages.error(request, f'Error al actualizar cupón: {str(e)}')
    
    context = {'cupon': cupon}
    return render(request, 'ZoneAdmin/admin_editar_cupon.html', context)


@login_required
def admin_eliminar_cupon(request, cupon_id):
    """Vista para eliminar un cupón"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    if request.method == 'POST':
        cupon = get_object_or_404(Cupon, id=cupon_id)
        codigo = cupon.codigo
        cupon.delete()
        messages.success(request, f'Cupón {codigo} eliminado exitosamente')
    
    return redirect('admin_cupones')


@login_required
def admin_toggle_cupon(request, cupon_id):
    """Vista para activar/desactivar un cupón"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No tienes permisos'})
    
    if request.method == 'POST':
        cupon = get_object_or_404(Cupon, id=cupon_id)
        cupon.activo = not cupon.activo
        cupon.save()
        
        return JsonResponse({
            'success': True,
            'activo': cupon.activo,
            'mensaje': f'Cupón {"activado" if cupon.activo else "desactivado"} correctamente'
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# SECCIÓN DE ANUNCIOS

@login_required
def admin_anuncios(request):
    """Vista para listar todos los anuncios"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    anuncios = Anuncio.objects.all().order_by('-fecha_creacion')
    
    context = {
        'anuncios': anuncios,
    }
    
    return render(request, 'ZoneAdmin/admin_anuncios.html', context)


@login_required
def admin_crear_anuncio(request):
    """Vista para crear un nuevo anuncio"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            anuncio = Anuncio.objects.create(
                texto=request.POST.get('texto'),
                enlace=request.POST.get('enlace', ''),
                texto_enlace=request.POST.get('texto_enlace', 'Ver más'),
                activo=request.POST.get('activo') == 'on',
                fecha_inicio=request.POST.get('fecha_inicio') or None,
                fecha_fin=request.POST.get('fecha_fin') or None,
            )
            messages.success(request, f'Anuncio creado exitosamente')
            return redirect('admin_anuncios')
        except Exception as e:
            messages.error(request, f'Error al crear anuncio: {str(e)}')
    
    return render(request, 'ZoneAdmin/admin_crear_anuncio.html')


@login_required
def admin_editar_anuncio(request, anuncio_id):
    """Vista para editar un anuncio existente"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    anuncio = get_object_or_404(Anuncio, id=anuncio_id)
    
    if request.method == 'POST':
        try:
            anuncio.titulo = request.POST.get('titulo')
            anuncio.descripcion = request.POST.get('descripcion', '')
            anuncio.enlace = request.POST.get('enlace', '')
            anuncio.orden = request.POST.get('orden', 0)
            anuncio.activo = request.POST.get('activo') == 'on'
            anuncio.fecha_inicio = request.POST.get('fecha_inicio') or None
            anuncio.fecha_fin = request.POST.get('fecha_fin') or None
            
            if request.FILES.get('imagen'):
                anuncio.imagen = request.FILES.get('imagen')
            
            anuncio.save()
            messages.success(request, f'Anuncio "{anuncio.titulo}" actualizado exitosamente')
            return redirect('admin_anuncios')
        except Exception as e:
            messages.error(request, f'Error al actualizar anuncio: {str(e)}')
    
    context = {'anuncio': anuncio}
    return render(request, 'ZoneAdmin/admin_editar_anuncio.html', context)


@login_required
def admin_eliminar_anuncio(request, anuncio_id):
    """Vista para eliminar un anuncio"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    if request.method == 'POST':
        anuncio = get_object_or_404(Anuncio, id=anuncio_id)
        titulo = anuncio.titulo
        anuncio.delete()
        messages.success(request, f'Anuncio "{titulo}" eliminado exitosamente')
    
    return redirect('admin_anuncios')


@login_required
def admin_toggle_anuncio(request, anuncio_id):
    """Vista para activar/desactivar un anuncio"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No tienes permisos'})
    
    if request.method == 'POST':
        anuncio = get_object_or_404(Anuncio, id=anuncio_id)
        anuncio.activo = not anuncio.activo
        anuncio.save()
        
        return JsonResponse({
            'success': True,
            'activo': anuncio.activo,
            'mensaje': f'Anuncio {"activado" if anuncio.activo else "desactivado"} correctamente'
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# SECCIÓN DE CURSOS

def lista_cursos(request):
    """Vista para listar todos los cursos online disponibles"""
    # Mostrar todos los cursos activos, sin importar la fecha
    # Esto permite ver cursos pasados, presentes y futuros
    cursos = Curso.objects.filter(activo=True).order_by('fecha_inicio')
    
    # Debug: Imprimir información de los cursos
    print(f"DEBUG: Total de cursos activos: {cursos.count()}")
    for curso in cursos:
        print(f"  - {curso.nombre}: inicio={curso.fecha_inicio}, termino={curso.fecha_termino}")
    
    context = {
        'cursos': cursos
    }
    
    return render(request, 'ZoneCursos/lista_cursos.html', context)


def detalle_curso(request, curso_id):
    """Vista para ver el detalle de un curso"""
    curso = get_object_or_404(Curso, id=curso_id)
    
    ya_inscrito = False
    inscripcion = None
    
    if request.user.is_authenticated:
        try:
            inscripcion = InscripcionCurso.objects.get(
                curso=curso, 
                usuario=request.user,
                estado='confirmada'
            )
            ya_inscrito = True
        except InscripcionCurso.DoesNotExist:
            pass
    
    context = {
        'curso': curso,
        'ya_inscrito': ya_inscrito,
        'inscripcion': inscripcion
    }
    
    return render(request, 'ZoneCursos/detalle_curso.html', context)


@login_required
def inscribir_curso(request, curso_id):
    """Vista para agregar un curso al carrito"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Verificar si ya está inscrito (solo confirmadas)
    inscripcion_existente = InscripcionCurso.objects.filter(
        curso=curso, 
        usuario=request.user,
        estado='confirmada'
    ).first()
    
    if inscripcion_existente:
        return JsonResponse({
            'success': False, 
            'message': 'Ya estás inscrito en este curso'
        })
    
    # Verificar cupos disponibles
    if not curso.tiene_cupos:
        return JsonResponse({
            'success': False, 
            'message': 'No hay cupos disponibles para este curso'
        })
    
    # Obtener o crear el carrito
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    
    # Verificar si el curso ya está en el carrito
    item_existente = CarritoItem.objects.filter(
        carrito=carrito,
        curso=curso
    ).first()
    
    if item_existente:
        return JsonResponse({
            'success': False,
            'message': 'Este curso ya está en tu carrito'
        })
    
    # Agregar el curso al carrito
    item = CarritoItem.objects.create(
        carrito=carrito,
        curso=curso,
        cantidad=1
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Curso agregado al carrito. Procede al pago para confirmar tu inscripción.',
        'redirect_url': reverse('ver_carrito')
    })


@login_required
def mis_cursos(request):
    """Vista para ver los cursos del usuario"""
    inscripciones = InscripcionCurso.objects.filter(
        usuario=request.user,
        estado='confirmada'
    ).select_related('curso', 'curso__matrona').order_by('-fecha_inscripcion')
    
    context = {
        'inscripciones': inscripciones
    }
    
    return render(request, 'ZoneCursos/mis_cursos.html', context)


@login_required
def panel_usuario(request):
    """Panel principal del usuario para ver sus compras"""
    # Obtener reservas confirmadas (servicios pagados)
    mis_reservas = Reservas.objects.filter(
        usuario=request.user,
        estado='C'  # Solo confirmadas/pagadas
    ).select_related('servicio', 'matrona').order_by('-fecha', '-hora_inicio')
    
    # Obtener inscripciones a cursos confirmadas
    mis_inscripciones = InscripcionCurso.objects.filter(
        usuario=request.user,
        estado='confirmada'
    ).select_related('curso', 'curso__matrona').order_by('-fecha_inscripcion')
    
    # Estadísticas
    total_servicios = mis_reservas.count()
    total_cursos = mis_inscripciones.count()
    
    # Próximas citas (futuras)
    from datetime import date
    proximas_citas = mis_reservas.filter(fecha__gte=date.today())[:5]
    
    context = {
        'mis_reservas': mis_reservas,
        'mis_inscripciones': mis_inscripciones,
        'total_servicios': total_servicios,
        'total_cursos': total_cursos,
        'proximas_citas': proximas_citas,
    }
    
    return render(request, 'ZoneUsuarios/panel_usuario.html', context)


@login_required
def cursos_matrona(request):
    """Vista para que la matrona vea sus cursos"""
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    cursos = Curso.objects.filter(matrona=request.user).order_by('-fecha_creacion')
    
    # Calcular total de inscritos en todos los cursos
    total_inscritos = sum(curso.cupos_ocupados for curso in cursos)
    
    # Calcular cursos activos (visibles)
    cursos_activos = cursos.filter(activo=True).count()
    
    context = {
        'cursos': cursos,
        'total_inscritos': total_inscritos,
        'cursos_activos': cursos_activos,
    }
    
    return render(request, 'ZoneMatronas/cursos_matrona.html', context)


@login_required
def crear_curso(request):
    """Vista para que la matrona cree un curso"""
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            curso = Curso.objects.create(
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion'),
                precio=request.POST.get('precio'),
                duracion_horas=request.POST.get('duracion_horas'),
                cupos_disponibles=request.POST.get('cupos_disponibles'),
                requisitos=request.POST.get('requisitos', ''),
                contenido=request.POST.get('contenido', ''),
                link_reunion=request.POST.get('link_reunion', ''),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_termino=request.POST.get('fecha_termino'),
                matrona=request.user
            )
            
            # Manejar imágenes
            img_list = request.FILES.getlist('imagenes')
            imgprincipal = int(request.POST.get('imgprincipal', 0))
            for i, imgfile in enumerate(img_list):
                ImagenCurso.objects.create(curso=curso, imagen=imgfile, es_principal=(i == imgprincipal))
            
            messages.success(request, f'Curso "{curso.nombre}" creado exitosamente')
            return redirect('cursos_matrona')
        except Exception as e:
            messages.error(request, f'Error al crear curso: {str(e)}')
    
    return render(request, 'ZoneMatronas/crear_curso.html')


@login_required
def editar_curso(request, curso_id):
    """Vista para editar un curso"""
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    curso = get_object_or_404(Curso, id=curso_id, matrona=request.user)
    
    if request.method == 'POST':
        try:
            curso.nombre = request.POST.get('nombre')
            curso.descripcion = request.POST.get('descripcion')
            # Asegurarse de que el precio no se pierda
            precio = request.POST.get('precio')
            if precio:
                curso.precio = precio
            curso.duracion_horas = request.POST.get('duracion_horas')
            # Validar que cupos no sean menores a los ocupados
            cupos = int(request.POST.get('cupos_disponibles'))
            if cupos < curso.cupos_ocupados:
                messages.error(request, f'No puedes reducir los cupos por debajo de {curso.cupos_ocupados} (cupos ya ocupados)')
                return redirect('editar_curso', curso_id=curso.id)
            curso.cupos_disponibles = cupos
            curso.requisitos = request.POST.get('requisitos', '')
            curso.contenido = request.POST.get('contenido', '')
            curso.link_reunion = request.POST.get('link_reunion', '')
            curso.fecha_inicio = request.POST.get('fecha_inicio')
            curso.fecha_termino = request.POST.get('fecha_termino')
            # Mantener el estado activo si no se especifica lo contrario
            curso.activo = request.POST.get('activo', 'on') == 'on'
            curso.save()
            
            # Manejar nuevas imágenes
            img_list = request.FILES.getlist('imagenes')
            for img in img_list:
                ImagenCurso.objects.create(curso=curso, imagen=img, es_principal=False)
            
            messages.success(request, f'Curso "{curso.nombre}" actualizado exitosamente')
            return redirect('cursos_matrona')
        except Exception as e:
            messages.error(request, f'Error al actualizar curso: {str(e)}')
    
    context = {'curso': curso}
    return render(request, 'ZoneMatronas/editar_curso.html', context)


@login_required
def toggle_curso(request, curso_id):
    """Vista para activar/desactivar un curso (mostrar/ocultar)"""
    if request.user.rol != 'matrona':
        return JsonResponse({'success': False, 'message': 'No tienes permisos'})
    
    if request.method == 'POST':
        curso = get_object_or_404(Curso, id=curso_id, matrona=request.user)
        curso.activo = not curso.activo
        curso.save()
        
        estado = 'visible' if curso.activo else 'oculto'
        return JsonResponse({
            'success': True, 
            'message': f'Curso "{curso.nombre}" ahora está {estado}',
            'activo': curso.activo
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def eliminar_curso(request, curso_id):
    """Vista para eliminar permanentemente un curso"""
    if request.user.rol != 'matrona':
        return JsonResponse({'success': False, 'message': 'No tienes permisos'})
    
    if request.method == 'POST':
        curso = get_object_or_404(Curso, id=curso_id, matrona=request.user)
        
        # Verificar si tiene inscripciones confirmadas
        if curso.inscripciones.filter(estado='confirmada').exists():
            return JsonResponse({
                'success': False, 
                'message': 'No puedes eliminar un curso con inscripciones confirmadas. Usa la opción de ocultar.'
            })
        
        nombre = curso.nombre
        curso.delete()
        return JsonResponse({
            'success': True,
            'message': f'Curso "{nombre}" eliminado exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def inscritos_curso(request, curso_id):
    """Vista para que la matrona vea los inscritos en su curso"""
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    curso = get_object_or_404(Curso, id=curso_id, matrona=request.user)
    inscripciones = InscripcionCurso.objects.filter(curso=curso).select_related('usuario').order_by('-fecha_inscripcion')
    
    context = {
        'curso': curso,
        'inscripciones': inscripciones
    }
    
    return render(request, 'ZoneMatronas/inscritos_curso.html', context)


@login_required
def lista_pacientes_matrona(request):
    """Vista para listar los pacientes de una matrona"""
    # Verificar si el usuario tiene perfil de matrona
    try:
        matrona_perfil = request.user.perfil_matrona
    except:

        return redirect('home')
    
    # Obtener pacientes únicos que tienen reservas con esta matrona
    reservas = Reservas.objects.filter(matrona=request.user, estado='C').select_related('usuario')
    pacientes_ids = reservas.values_list('usuario_id', flat=True).distinct()
    pacientes = Usuario.objects.filter(id__in=pacientes_ids)
    
    # Agregar campo calculado para verificar si tiene ficha clínica
    for paciente in pacientes:
        paciente.tiene_ficha_clinica = FichaClinica.objects.filter(paciente=paciente).exists()
    
    # Estadísticas
    hoy = timezone.now().date()
    reservas_hoy = Reservas.objects.filter(
        matrona=request.user,
        fecha=hoy,
        estado='C'
    ).count()
    
    primer_dia_mes = hoy.replace(day=1)
    reservas_mes = Reservas.objects.filter(
        matrona=request.user,
        fecha__gte=primer_dia_mes,
        fecha__lte=hoy,
        estado='C'
    ).count()
    
    context = {
        'pacientes': pacientes,
        'reservas_hoy': reservas_hoy,
        'reservas_mes': reservas_mes,
        'total_pacientes': pacientes.count(),
    }
    
    return render(request, 'ZoneMatronas/listaPacientes.html', context)


@login_required
def crear_ficha_clinica(request):
    """Vista para crear una ficha clínica"""
    if request.method == 'POST':
        # Verificar si el usuario tiene perfil de matrona
        try:
            matrona_perfil = request.user.perfil_matrona
        except:
            messages.error(request, 'No tienes permisos para realizar esta acción')
            return redirect('home')
        
        paciente_id = request.POST.get('paciente_id')
        paciente = get_object_or_404(Usuario, id=paciente_id)
        
        # Verificar que no exista ya una ficha clínica
        if FichaClinica.objects.filter(paciente=paciente).exists():
            messages.warning(request, 'Este paciente ya tiene una ficha clínica')
            return redirect('lista_pacientes_matrona')
        
        # Crear la ficha clínica
        ficha = FichaClinica.objects.create(
            paciente=paciente,
            matrona=matrona_perfil,
            antecedentes_medicos=request.POST.get('antecedentes_medicos', ''),
            medicacion_actual=request.POST.get('medicacion_actual', ''),
            observaciones=request.POST.get('observaciones', '')
        )
        
        return redirect('lista_pacientes_matrona')
    
    return redirect('lista_pacientes_matrona')


@login_required
def ver_ficha_clinica(request, paciente_id):
    """Vista para ver la ficha clínica de un paciente"""
    # Verificar si el usuario tiene perfil de matrona
    try:
        matrona_perfil = request.user.perfil_matrona
    except:

        return redirect('home')
    
    paciente = get_object_or_404(Usuario, id=paciente_id)
    ficha = get_object_or_404(FichaClinica, paciente=paciente)
    
    context = {
        'paciente': paciente,
        'ficha': ficha
    }
    
    return render(request, 'ZoneMatronas/fichaClinica.html', context)


@login_required
def editar_ficha_clinica(request, paciente_id):
    """Vista para editar la ficha clínica de un paciente"""
    # Verificar si el usuario tiene perfil de matrona
    try:
        matrona_perfil = request.user.perfil_matrona
    except:

        return redirect('home')
    
    paciente = get_object_or_404(Usuario, id=paciente_id)
    ficha = get_object_or_404(FichaClinica, paciente=paciente)
    
    if request.method == 'POST':
        # Actualizar la ficha clínica
        ficha.antecedentes_medicos = request.POST.get('antecedentes_medicos', '')
        ficha.medicacion_actual = request.POST.get('medicacion_actual', '')
        ficha.observaciones = request.POST.get('observaciones', '')
        ficha.save()
        
        return redirect('ver_ficha_clinica', paciente_id=paciente.id)
    
    context = {
        'paciente': paciente,
        'ficha': ficha
    }
    
    return render(request, 'ZoneMatronas/editarFichaClinica.html', context)


@login_required
def detalle_paciente(request, paciente_id):
    """Vista para ver el detalle de un paciente"""
    # Verificar si el usuario tiene perfil de matrona
    try:
        matrona_perfil = request.user.perfil_matrona
    except:

        return redirect('home')
    
    paciente = get_object_or_404(Usuario, id=paciente_id)
    
    # Verificar que el paciente tenga reservas con esta matrona
    tiene_reservas = Reservas.objects.filter(
        usuario=paciente,
        matrona=request.user,
        estado='C'
    ).exists()
    
    if not tiene_reservas:
        messages.error(request, 'No tienes acceso a este paciente')
        return redirect('lista_pacientes_matrona')
    
    # Obtener reservas del paciente con esta matrona
    reservas = Reservas.objects.filter(
        usuario=paciente,
        matrona=request.user
    ).select_related('servicio').order_by('-fecha', '-hora_inicio')
    
    # Verificar si tiene ficha clínica
    tiene_ficha = FichaClinica.objects.filter(paciente=paciente).exists()
    
    context = {
        'paciente': paciente,
        'reservas': reservas,
        'tiene_ficha': tiene_ficha
    }
    
    return render(request, 'ZoneMatronas/detallePaciente.html', context)


@login_required
def historial_paciente(request, paciente_id):
    """Vista para ver el historial médico de un paciente"""
    # Verificar si el usuario tiene perfil de matrona
    try:
        matrona_perfil = request.user.perfil_matrona
    except:

        return redirect('home')
    
    paciente = get_object_or_404(Usuario, id=paciente_id)
    
    # Verificar acceso
    tiene_acceso = Reservas.objects.filter(
        usuario=paciente,
        matrona=request.user,
        estado='C'
    ).exists()
    
    if not tiene_acceso:
        messages.error(request, 'No tienes acceso a este paciente')
        return redirect('lista_pacientes_matrona')
    
    # Obtener todas las reservas
    reservas = Reservas.objects.filter(
        usuario=paciente,
        matrona=request.user
    ).select_related('servicio').order_by('-fecha', '-hora_inicio')
    
    # Obtener ficha clínica si existe
    ficha_clinica = FichaClinica.objects.filter(paciente=paciente).first()
    
    context = {
        'paciente': paciente,
        'reservas': reservas,
        'ficha_clinica': ficha_clinica
    }
    
    return render(request, 'ZoneMatronas/historialPaciente.html', context)

@require_http_methods(["GET"])
def info_matrona(request, matrona_id):
    """Vista para obtener información de una matrona en formato JSON"""
    try:
        matrona = Matrona.objects.select_related('usuario').get(id=matrona_id)
        data = {
            'id': matrona.id,
            'nombre': matrona.usuario.get_full_name(),
            'descripcion': matrona.descripcion or '',
            'email': matrona.usuario.email or '',
            'color_agenda': matrona.color_agenda,
            'foto_perfil': matrona.foto_perfil.url if matrona.foto_perfil else None
        }
        return JsonResponse(data)
    except Matrona.DoesNotExist:
        return JsonResponse({'error': 'Matrona no encontrada'}, status=404)

@login_required
def admin_gestionar_usuarios(request):
    """Vista para que admin gestione usuarios y asigne rol de matrona"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
    # Obtener todos los usuarios
    usuarios = Usuario.objects.all().order_by('-date_joined')
    
    # Filtros opcionales
    rol_filtro = request.GET.get('rol', '')
    busqueda = request.GET.get('busqueda', '')
    
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(email__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(rut__icontains=busqueda)
        )
    
    # Contar usuarios por rol
    total_matronas = usuarios.filter(rol='matrona').count()
    total_usuarios = usuarios.filter(rol='usuario').count()
    
    context = {
        'usuarios': usuarios,
        'rol_filtro': rol_filtro,
        'busqueda': busqueda,
        'total_matronas': total_matronas,
        'total_usuarios': total_usuarios,
    }
    
    return render(request, 'ZoneAdmin/gestionar_usuarios.html', context)

@login_required
@require_POST
def admin_cambiar_rol_usuario(request, usuario_id):
    """Vista para cambiar el rol de un usuario"""
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Sin permisos'}, status=403)
    
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        nuevo_rol = request.POST.get('rol')
        
        if nuevo_rol not in ['usuario', 'matrona']:
            return JsonResponse({'success': False, 'message': 'Rol inválido'}, status=400)
        
        # Si cambia a matrona y no tiene perfil de matrona, crearlo
        if nuevo_rol == 'matrona' and not hasattr(usuario, 'perfil_matrona'):
            Matrona.objects.create(
                usuario=usuario,
                telefono=usuario.telefono or '',
                descripcion='',
                color_agenda='#7436ad'
            )
            messages.success(request, f'Perfil de matrona creado para {usuario.get_full_name()}')
        
        usuario.rol = nuevo_rol
        usuario.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Rol cambiado a {nuevo_rol}',
            'nuevo_rol': nuevo_rol
        })
        
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# ==================== VISTAS DE RULETA ====================

@login_required
def admin_ruleta(request):
    """Vista para listar beneficios de la ruleta"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    beneficios = RuletaBeneficio.objects.all().order_by('orden', '-fecha_creacion')
    
    context = {
        'beneficios': beneficios,
    }
    
    return render(request, 'ZoneAdmin/admin_ruleta.html', context)


@login_required
def admin_crear_beneficio_ruleta(request):
    """Vista para crear un nuevo beneficio de ruleta"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            tipo = request.POST.get('tipo_beneficio')
            
            beneficio = RuletaBeneficio.objects.create(
                texto=request.POST.get('texto'),
                tipo_beneficio=tipo,
                cupon_id=request.POST.get('cupon') if tipo == 'cupon' else None,
                valor_porcentaje=request.POST.get('valor_porcentaje') if tipo == 'porcentaje' else None,
                valor_monto=request.POST.get('valor_monto') if tipo == 'monto' else None,
                probabilidad=request.POST.get('probabilidad', 10),
                color=request.POST.get('color', '#E982F2'),
                orden=request.POST.get('orden', 0),
                activo=request.POST.get('activo') == 'on',
            )
            messages.success(request, f'Beneficio "{beneficio.texto}" creado exitosamente')
            return redirect('admin_ruleta')
        except Exception as e:
            messages.error(request, f'Error al crear beneficio: {str(e)}')
    
    cupones = Cupon.objects.filter(activo=True)
    context = {'cupones': cupones}
    return render(request, 'ZoneAdmin/admin_crear_beneficio_ruleta.html', context)


@login_required
def admin_editar_beneficio_ruleta(request, beneficio_id):
    """Vista para editar un beneficio de ruleta"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    beneficio = get_object_or_404(RuletaBeneficio, id=beneficio_id)
    
    if request.method == 'POST':
        try:
            tipo = request.POST.get('tipo_beneficio')
            
            beneficio.texto = request.POST.get('texto')
            beneficio.tipo_beneficio = tipo
            beneficio.cupon_id = request.POST.get('cupon') if tipo == 'cupon' else None
            beneficio.valor_porcentaje = request.POST.get('valor_porcentaje') if tipo == 'porcentaje' else None
            beneficio.valor_monto = request.POST.get('valor_monto') if tipo == 'monto' else None
            beneficio.probabilidad = request.POST.get('probabilidad', 10)
            beneficio.color = request.POST.get('color', '#E982F2')
            beneficio.orden = request.POST.get('orden', 0)
            beneficio.activo = request.POST.get('activo') == 'on'
            
            beneficio.save()
            messages.success(request, f'Beneficio "{beneficio.texto}" actualizado exitosamente')
            return redirect('admin_ruleta')
        except Exception as e:
            messages.error(request, f'Error al actualizar beneficio: {str(e)}')
    
    cupones = Cupon.objects.filter(activo=True)
    context = {
        'beneficio': beneficio,
        'cupones': cupones,
    }
    return render(request, 'ZoneAdmin/admin_editar_beneficio_ruleta.html', context)


@login_required
def admin_eliminar_beneficio_ruleta(request, beneficio_id):
    """Vista para eliminar un beneficio de ruleta"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos de administrador')
        return redirect('home')
    
    beneficio = get_object_or_404(RuletaBeneficio, id=beneficio_id)
    texto = beneficio.texto
    beneficio.delete()
    
    messages.success(request, f'Beneficio "{texto}" eliminado exitosamente')
    return redirect('admin_ruleta')


@login_required
def admin_toggle_beneficio_ruleta(request, beneficio_id):
    """Vista AJAX para activar/desactivar un beneficio"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)
    
    try:
        beneficio = RuletaBeneficio.objects.get(id=beneficio_id)
        beneficio.activo = not beneficio.activo
        beneficio.save()
        
        return JsonResponse({
            'success': True,
            'activo': beneficio.activo,
            'message': f'Beneficio {"activado" if beneficio.activo else "desactivado"}'
        })
    except RuletaBeneficio.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Beneficio no encontrado'}, status=404)


@login_required
def verificar_ruleta(request):
    """Vista AJAX para verificar si el usuario puede girar la ruleta"""
    try:
        participacion, created = UsuarioRuleta.objects.get_or_create(usuario=request.user)
        
        beneficios = list(RuletaBeneficio.objects.filter(activo=True).values(
            'id', 'texto', 'color', 'probabilidad'
        ))
        
        return JsonResponse({
            'puede_girar': not participacion.ha_girado,
            'beneficios': beneficios,
            'total_probabilidad': sum(b['probabilidad'] for b in beneficios)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def girar_ruleta(request):
    """Vista POST para girar la ruleta y obtener un beneficio"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        import random
        from django.utils import timezone
        
        # Verificar si ya giró
        participacion, created = UsuarioRuleta.objects.get_or_create(usuario=request.user)
        
        if participacion.ha_girado:
            return JsonResponse({
                'success': False,
                'message': 'Ya has girado la ruleta anteriormente'
            }, status=400)
        
        # Obtener beneficios activos
        beneficios = list(RuletaBeneficio.objects.filter(activo=True))
        
        if not beneficios:
            return JsonResponse({
                'success': False,
                'message': 'No hay beneficios disponibles en este momento'
            }, status=400)
        
        # Seleccionar beneficio según probabilidad
        total_prob = sum(b.probabilidad for b in beneficios)
        rand = random.uniform(0, total_prob)
        acumulado = 0
        
        beneficio_ganado = None
        for beneficio in beneficios:
            acumulado += beneficio.probabilidad
            if rand <= acumulado:
                beneficio_ganado = beneficio
                break
        
        if not beneficio_ganado:
            beneficio_ganado = beneficios[-1]
        
        # Aplicar beneficio según tipo
        cupon_generado = None
        mensaje_beneficio = ""
        
        if beneficio_ganado.tipo_beneficio == 'cupon':
            cupon_generado = beneficio_ganado.cupon
            if cupon_generado.tipo_descuento == 'porcentaje':
                mensaje_beneficio = f'¡Ganaste el cupón {cupon_generado.codigo}! Descuento: {cupon_generado.valor_descuento}%'
            else:
                mensaje_beneficio = f'¡Ganaste el cupón {cupon_generado.codigo}! Descuento: ${cupon_generado.valor_descuento}'
        
        elif beneficio_ganado.tipo_beneficio == 'porcentaje':
            # Crear cupón temporal único
            codigo_unico = f'RULETA{request.user.id}{timezone.now().strftime("%Y%m%d%H%M%S")}'
            cupon_generado = Cupon.objects.create(
                codigo=codigo_unico,
                tipo_descuento='porcentaje',
                valor_descuento=beneficio_ganado.valor_porcentaje,
                usos_maximos=1,
                activo=True,
                fecha_inicio=timezone.now(),
                fecha_expiracion=timezone.now() + timezone.timedelta(days=30)
            )
            mensaje_beneficio = f'¡Ganaste {beneficio_ganado.valor_porcentaje}% de descuento! Cupón: {codigo_unico}'
        
        elif beneficio_ganado.tipo_beneficio == 'monto':
            # Crear cupón con monto fijo
            codigo_unico = f'RULETA{request.user.id}{timezone.now().strftime("%Y%m%d%H%M%S")}'
            cupon_generado = Cupon.objects.create(
                codigo=codigo_unico,
                tipo_descuento='fijo',
                valor_descuento=beneficio_ganado.valor_monto,
                usos_maximos=1,
                activo=True,
                fecha_inicio=timezone.now(),
                fecha_expiracion=timezone.now() + timezone.timedelta(days=30)
            )
            mensaje_beneficio = f'¡Ganaste ${beneficio_ganado.valor_monto} de descuento! Cupón: {codigo_unico}'
        
        # Registrar participación
        participacion.ha_girado = True
        participacion.beneficio_obtenido = beneficio_ganado
        participacion.cupon_generado = cupon_generado
        participacion.fecha_giro = timezone.now()
        participacion.save()
        
        return JsonResponse({
            'success': True,
            'beneficio': {
                'id': beneficio_ganado.id,
                'texto': beneficio_ganado.texto,
                'tipo': beneficio_ganado.tipo_beneficio,
                'color': beneficio_ganado.color,
                'mensaje': mensaje_beneficio,
                'codigo_cupon': cupon_generado.codigo if cupon_generado else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
