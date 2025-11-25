from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse, Http404
from .forms import UsuarioForm, EmailAuthenticationForm, ServicioForm, ServicioImagenForm, seleccionarServicioForm, disponibilidadServicioFormSet, ContactoForm, PerfilMatronaForm
from .models import BloqueServicio, Usuario, Servicio, ImagenServicio, disponibilidadServicio, Reservas, Carrito, CarritoItem, Matrona, Venta, Pagos
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime, timedelta
from django.db import transaction
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
        'servicio'
    ).prefetch_related('servicio__imagenes')
    
    # Agregar información de reservas si existen
    for item in items:
        try:
            item.reserva_asociada = Reservas.objects.get(carrito_item=item)
        except Reservas.DoesNotExist:
            item.reserva_asociada = None
    
    context = {'carrito': carrito, 'items': items}
    return render(request, 'ZoneServicios/carrito.html', context)

@login_required
def eliminarItemCarrito(request, item_id):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
    
    with transaction.atomic():
        try:
            reserva = Reservas.objects.get(carrito_item=item)
            reserva.estado = 'X'  # Cancelada/Expirada
            reserva.carrito_item = None
            reserva.save()
        except Reservas.DoesNotExist:
            pass
        item.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'item_id': item_id, 'total': carrito.total})
    return redirect('ver_carrito')


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


### ========== SECCIÓN WEBPAY ==========

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
            items = CarritoItem.objects.filter(carrito=carrito).select_related('servicio')
            
            reservas_info = []
            for item in items:
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
            
            # Ahora actualizar la base de datos
            with transaction.atomic():
                pago.estado = 'APROBADO'
                pago.codigo_autorizacion = response.get('authorization_code', '')
                pago.tipo_pago = response.get('payment_type_code', '')
                pago.save()
                
                venta.estado = 'CONFIRMADA'
                venta.save()
                
                for item in items:
                    try:
                        reserva = Reservas.objects.get(carrito_item=item)
                        reserva.estado = 'C'
                        reserva.save()
                    except Reservas.DoesNotExist:
                        pass
                
                items.delete()
            
            # Preparar y enviar correo
            usuario = venta.rut
            nombre_completo = usuario.get_full_name() or usuario.email
            
            if reservas_info:
                detalles_servicios = "\n".join([
                    f"• {info['servicio_nombre']}\n"
                    f"  Fecha: {info['fecha']}\n"
                    f"  Hora: {info['hora_inicio']} - {info['hora_fin']}\n"
                    f"  Matrona: {info['matrona']}\n"
                    for info in reservas_info
                ])
            else:
                detalles_servicios = "No se encontraron detalles"
            
            subject = '✅ Reserva Confirmada - ZoneFem'
            message = f'''
Hola {nombre_completo},

¡Tu pago ha sido procesado exitosamente!

📋 DETALLES DE TU COMPRA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• ID de Venta: {venta.id}
• Total Pagado: ${venta.total_venta:,} CLP
• Fecha de Pago: {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}

📅 TUS RESERVAS CONFIRMADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{detalles_servicios}
‼️¡IMPORTANTE! La matrona se contactará contigo para enviarte el link de la reunión en las próximas horas😎

🤞Recuerda estar en un lugar sin ruido, para que nuestra comunicación sea la optima😊.

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
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
                html_message=message
            )
            
            # messages.success(request, 'Te hemos enviado un correo con instrucciones para restablecer tu contraseña.')
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
def perfil_matrona(request):
    if request.user.rol != 'matrona':
        messages.error(request, 'No tienes permisos')
        return redirect('home')
    
    perfil_matrona = request.user.perfil_matrona
    
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


