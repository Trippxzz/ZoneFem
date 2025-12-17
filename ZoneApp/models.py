from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager, Group, Permission
from django.utils import timezone
from django.core.exceptions import ValidationError
import magic
from datetime import date
# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class Usuario(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=False, verbose_name='Nombre')
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT") # Esto cambia el nombre en el Admin
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    telefono = models.CharField(max_length=12,null=True, blank=True)
    USERNAME_FIELD = 'email' # Para que se pida el correo para iniciar sesión
    REQUIRED_FIELDS = ['first_name', 'rut']
    # fichaclinica
    objects = UsuarioManager()
    ROLES_CHOICES = (('matrona', 'matrona'), ('usuario', 'usuario'),)
    rol = models.CharField(max_length=10,  choices=ROLES_CHOICES, default='usuario', verbose_name='Rol') # El rol default será cliente, la admin deberá dar rol Matrona
    ###PARA NO TENER ERRORES
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to.'
        ),
        # Usamos 'usuario_groups' para evitar el choque
        related_name="usuario_groups", 
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        # Usamos 'usuario_permissions' para evitar el choque
        related_name="usuario_permissions",
    )

    def __str__(self):
        return self.email

    def calcular_edad(self):
        if not self.fecha_nacimiento:
            return None
        
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        
        return edad
    
    @property
    def edad(self):
        return self.calcular_edad()

def validate_image(file): ##PARA VALIDAR IMAGENES | SEGURIDAD
    file_type = magic.from_buffer(file.read(1024), mime=True)
    if file_type not in ['image/jpeg', 'image/png', 'image/gif']:
        raise ValidationError('Solo se permiten imágenes JPG, PNG o GIF')
    file.seek(0)
    
    # Validar tamaño
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('La imagen no puede superar 5MB')

class Matrona(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_matrona', verbose_name='Usuario Matrona')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono de Contacto')
    descripcion = models.TextField(verbose_name='Descripción/Especialidad', blank=True)
    color_agenda = models.CharField(
            max_length=7, 
            default="#7436ad", 
            verbose_name='Color en Agenda'
        )
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True, verbose_name='Foto de Perfil', validators=[validate_image])
    fecha_registro = models.DateTimeField(default=timezone.now)
    class Meta:
        verbose_name = 'Matrona'
        verbose_name_plural = 'Matronas'
    def __str__(self):
        # Accedemos al RUT a través del usuario
        return f"Matrona: {self.usuario.first_name} ({self.usuario.rut})"
    def get_full_name(self):
        return self.usuario.get_full_name()
    
class Servicio(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Servicio')
    descripcion = models.TextField(verbose_name='Descripción del Servicio')
    precio = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Precio del Servicio')
    duracion = models.IntegerField(verbose_name='Duración en minutos')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return self.nombre
    
    def imagen_principal(self):
        return self.imagenes.filter(es_principal=True).first()
    
    def calificacion_promedio(self):
        """Calcula el promedio de calificaciones"""
        opiniones = self.opiniones.all()
        if opiniones.exists():
            return round(sum(op.calificacion for op in opiniones) / opiniones.count(), 1)
        return 0
    
    def total_opiniones(self):
        """Cuenta total de opiniones"""
        return self.opiniones.count()


class Curso(models.Model):
    MODALIDAD_CHOICES = (
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto/Online'),
        ('mixto', 'Mixto (Presencial + Online)'),
    )
    
    nombre = models.CharField(max_length=150, verbose_name='Nombre del Curso')
    descripcion = models.TextField(verbose_name='Descripción del Curso')
    precio = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Precio del Curso')
    duracion_horas = models.IntegerField(verbose_name='Duración Total (horas)')
    modalidad = models.CharField(max_length=15, choices=MODALIDAD_CHOICES, default='presencial', verbose_name='Modalidad')
    cupos_disponibles = models.PositiveIntegerField(default=20, verbose_name='Cupos Disponibles')
    
    # Información adicional
    requisitos = models.TextField(blank=True, verbose_name='Requisitos', help_text='Requisitos previos para el curso')
    contenido = models.TextField(blank=True, verbose_name='Contenido del Curso', help_text='Temario o módulos del curso')
    ubicacion = models.CharField(max_length=200, blank=True, verbose_name='Ubicación', help_text='Dirección si es presencial o mixto')
    link_reunion = models.URLField(blank=True, verbose_name='Link de Reunión', help_text='Zoom, Meet, etc. si es remoto o mixto')
    
    # Fechas
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_termino = models.DateField(verbose_name='Fecha de Término')
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    # Matrona que imparte el curso
    matrona = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cursos_impartidos', limit_choices_to={'rol': 'matrona'})
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_modalidad_display()}"
    
    def imagen_principal(self):
        return self.imagenes_curso.filter(es_principal=True).first()
    
    @property
    def cupos_ocupados(self):
        return self.inscripciones.filter(estado='confirmada').count()
    
    @property
    def cupos_restantes(self):
        return self.cupos_disponibles - self.cupos_ocupados
    
    @property
    def tiene_cupos(self):
        return self.cupos_ocupados < self.cupos_disponibles
    
    @property
    def porcentaje_ocupacion(self):
        if self.cupos_disponibles == 0:
            return 0
        return (self.cupos_ocupados / self.cupos_disponibles) * 100


class ImagenCurso(models.Model):
    curso = models.ForeignKey(Curso, related_name='imagenes_curso', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='cursos/', validators=[validate_image])
    es_principal = models.BooleanField(default=False, verbose_name='¿Imagen Principal?')

    def __str__(self):
        return f"Imagen de {self.curso.nombre}"
    
    def save(self, *args, **kwargs):
        if self.es_principal:
            ImagenCurso.objects.filter(curso=self.curso, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Imagen de Curso'
        verbose_name_plural = 'Imágenes de Cursos'


class InscripcionCurso(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente de Pago'),
        ('confirmada', 'Confirmada (Pagada)'),
        ('cancelada', 'Cancelada'),
    )
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cursos_inscritos')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente', verbose_name='Estado')
    
    # Información adicional
    comentarios = models.TextField(blank=True, verbose_name='Comentarios o Consultas')
    
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inscripción a Curso'
        verbose_name_plural = 'Inscripciones a Cursos'
        unique_together = ('curso', 'usuario')
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.curso.nombre} ({self.get_estado_display()})"
    
    
class ImagenServicio(models.Model):
    servicio = models.ForeignKey(Servicio, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='servicios/', validators=[validate_image])
    es_principal = models.BooleanField(default=False, verbose_name='¿Imagen Principal?')

    def __str__(self):
        return f"Imagen de {self.servicio.nombre}"
    
    def save(self, *args, **kwargs):
        if self.es_principal:
            ImagenServicio.objects.filter(servicio=self.servicio, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)


class OpinionServicio(models.Model):
    servicio = models.ForeignKey(Servicio, related_name='opiniones', on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calificacion = models.IntegerField(
        choices=[(1, '1 estrella'), (2, '2 estrellas'), (3, '3 estrellas'), (4, '4 estrellas'), (5, '5 estrellas')],
        verbose_name='Calificación'
    )
    comentario = models.TextField(verbose_name='Comentario')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        unique_together = ['servicio', 'usuario']
        ordering = ['-fecha_creacion']
        verbose_name = 'Opinión de Servicio'
        verbose_name_plural = 'Opiniones de Servicios'
    
    def __str__(self):
        return f"{self.usuario.email} - {self.servicio.nombre} ({self.calificacion}★)"


class BloqueServicio(models.Model):
    matrona = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='servicios_ofrecidos')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='bloques_matronas')

    class Meta:
        unique_together = ('matrona', 'servicio')

    def getDuracion(self):
        return self.servicio.duracion
    def __str__(self):
        # Esto hará que el dropdown muestre el nombre del servicio
        return self.servicio.nombre

class disponibilidadServicio(models.Model):
    bloque_servicio = models.ForeignKey(BloqueServicio, on_delete=models.CASCADE, related_name='disponibilidad')
    DIA_CHOICES = (
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )
    dia_semana = models.IntegerField(choices=DIA_CHOICES, verbose_name='Día de la Semana')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')

    class Meta:
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.bloque_servicio.matrona} ofrece {self.bloque_servicio.servicio} el {self.get_dia_semana_display()} de {self.hora_inicio} a {self.hora_fin}"


class Reservas(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas_hechas')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='reservas_servicio')
    matrona = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas_atendidas')
    fecha = models.DateField(verbose_name='Fecha de la Reserva')
    hora_inicio = models.TimeField(verbose_name='Hora de Inicio')
    hora_fin = models.TimeField(verbose_name='Hora de Fin')
    ESTADO_CHOICES = (
        ('P', 'Pendiente de Pago (en carrito)'), # Está en el carrito, bloqueando el slot
        ('C', 'Confirmada (Pagada)'),          # Pago exitoso, cita asegurada
        ('X', 'Cancelada/Expirada'),           # El cliente no pagó o la canceló
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P', verbose_name='Estado de la Reserva')

    carrito_item = models.OneToOneField('CarritoItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='reserva_asociada')
    fechacreacion = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['matrona', 'fecha', 'hora_inicio'], name = 'unique_reserva_slot')
        ]
    def __str__(self):
        return f"Reserva de {self.servicio.nombre} por {self.usuario.first_name} el {self.fecha} a las {self.hora_inicio}"
    
class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)
    cupon_aplicado = models.ForeignKey('Cupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='carritos')

    def __str__(self):
        return f"Carrito de {self.usuario.email}"
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def descuento(self):
        if self.cupon_aplicado:
            valido, mensaje = self.cupon_aplicado.es_valido(self.usuario, self.subtotal)
            if valido:
                return self.cupon_aplicado.calcular_descuento(self.subtotal)
        return 0
    
    @property
    def total(self):
        return self.subtotal - self.descuento
    
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='carrito_items', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='carrito_items', null=True, blank=True)
    cantidad= models.PositiveIntegerField(default=1, editable=False)
    
    def __str__(self):
        if self.servicio:
            return f"{self.cantidad} x {self.servicio.nombre} en el carrito de {self.carrito.id}"
        elif self.curso:
            return f"Curso: {self.curso.nombre} en el carrito de {self.carrito.id}"
        return f"Item en el carrito de {self.carrito.id}"
    
    @property
    def subtotal(self):
        if self.servicio:
            return self.servicio.precio * self.cantidad
        elif self.curso:
            return self.curso.precio
        return 0
    
    @property
    def nombre(self):
        if self.servicio:
            return self.servicio.nombre
        elif self.curso:
            return self.curso.nombre
        return "Item"
    
    @property
    def precio(self):
        if self.servicio:
            return self.servicio.precio
        elif self.curso:
            return self.curso.precio
        return 0


class Venta(models.Model):
    rut = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(default=timezone.now)
    total_venta = models.IntegerField()
    estado = models.CharField(
        max_length=20, 
        choices=[('PENDIENTE', 'Pendiente'), ('CONFIRMADA', 'Confirmada'), ('ANULADA', 'Anulada')],
        default='PENDIENTE'
    )###CAMPOS QUE FUNCIONAN CON LA INTEGRACIÓN DE TRANSBANK WEBPAY

class Pagos(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    monto_total = models.IntegerField()
    fecha_pago = models.DateTimeField(default=timezone.now)
    metodo_pago = models.CharField(max_length=50, default='WEBPAY')
    #TRANSBANK
    token_ws = models.CharField(max_length=255, unique=True, null=True) # El token vital
    tipo_pago = models.CharField(max_length=50, null=True, blank=True) # Crédito/Débito (te lo da TBK al volver)
    codigo_autorizacion = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(
        max_length=20, 
        choices=[('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')],
        default='PENDIENTE'
    )


class FichaClinica(models.Model):
    paciente = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='ficha_clinica')
    matrona = models.ForeignKey('Matrona', on_delete=models.SET_NULL, null=True, related_name='fichas_creadas')
    
    # Campos de la ficha
    observaciones = models.TextField(blank=True, help_text='Notas adicionales')
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ficha Clínica'
        verbose_name_plural = 'Fichas Clínicas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Ficha de {self.paciente.get_full_name()}'


class Cupon(models.Model):
    TIPO_DESCUENTO = (
        ('porcentaje', 'Porcentaje'),
        ('fijo', 'Monto Fijo'),
    )
    
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código del Cupón')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    tipo_descuento = models.CharField(max_length=15, choices=TIPO_DESCUENTO, default='porcentaje', verbose_name='Tipo de Descuento')
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor del Descuento')
    
    # Restricciones
    monto_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Monto Mínimo de Compra')
    usos_maximos = models.PositiveIntegerField(null=True, blank=True, verbose_name='Usos Máximos', help_text='Dejar en blanco para ilimitado')
    usos_actuales = models.PositiveIntegerField(default=0, verbose_name='Usos Actuales')
    usos_por_usuario = models.PositiveIntegerField(default=1, verbose_name='Usos por Usuario')
    
    # Fechas
    fecha_inicio = models.DateTimeField(verbose_name='Fecha de Inicio')
    fecha_expiracion = models.DateTimeField(verbose_name='Fecha de Expiración')
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cupón de Descuento'
        verbose_name_plural = 'Cupones de Descuento'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        if self.tipo_descuento == 'porcentaje':
            return f'{self.codigo} - {self.valor_descuento}% de descuento'
        else:
            return f'{self.codigo} - ${self.valor_descuento} de descuento'
    
    def es_valido(self, usuario=None, total_carrito=0):
        """Verifica si el cupón es válido"""
        ahora = timezone.now()
        
        # Verificar si está activo
        if not self.activo:
            return False, 'El cupón no está activo'
        
        # Verificar fechas
        if ahora < self.fecha_inicio:
            return False, 'El cupón aún no es válido'
        
        if ahora > self.fecha_expiracion:
            return False, 'El cupón ha expirado'
        
        # Verificar usos máximos
        if self.usos_maximos and self.usos_actuales >= self.usos_maximos:
            return False, 'El cupón ha alcanzado su límite de usos'
        
        # Verificar monto mínimo
        if self.monto_minimo and total_carrito < self.monto_minimo:
            return False, f'El monto mínimo de compra es ${self.monto_minimo}'
        
        # Verificar usos por usuario
        if usuario and usuario.is_authenticated:
            usos_usuario = UsoCupon.objects.filter(cupon=self, usuario=usuario).count()
            if usos_usuario >= self.usos_por_usuario:
                return False, 'Ya has usado este cupón el máximo de veces permitido'
        
        return True, 'Cupón válido'
    
    def calcular_descuento(self, total):
        """Calcula el monto de descuento"""
        if self.tipo_descuento == 'porcentaje':
            descuento = (total * self.valor_descuento) / 100
        else:
            descuento = self.valor_descuento
        
        # El descuento no puede ser mayor al total
        return min(descuento, total)


class UsoCupon(models.Model):
    cupon = models.ForeignKey(Cupon, on_delete=models.CASCADE, related_name='usos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cupones_usados')
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='cupon_aplicado', null=True, blank=True)
    fecha_uso = models.DateTimeField(auto_now_add=True)
    monto_descuento = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto del Descuento')
    
    class Meta:
        verbose_name = 'Uso de Cupón'
        verbose_name_plural = 'Usos de Cupones'
        ordering = ['-fecha_uso']
    
    def __str__(self):
        return f'{self.usuario.email} usó {self.cupon.codigo} el {self.fecha_uso.strftime("%d/%m/%Y")}'


class Anuncio(models.Model):
    texto = models.CharField(max_length=300, verbose_name='Texto del Anuncio')
    enlace = models.URLField(blank=True, null=True, verbose_name='Enlace (opcional)')
    texto_enlace = models.CharField(max_length=50, blank=True, default='Ver más', verbose_name='Texto del enlace')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_inicio = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de inicio')
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de fin')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Anuncio'
        verbose_name_plural = 'Anuncios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.texto[:50]
    
    def esta_vigente(self):
        """Verifica si el anuncio está dentro del rango de fechas"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.activo:
            return False
        
        if self.fecha_inicio and now < self.fecha_inicio:
            return False
        
        if self.fecha_fin and now > self.fecha_fin:
            return False
        
        return True


class RuletaBeneficio(models.Model):
    """Opciones de beneficios disponibles en la ruleta"""
    TIPO_CHOICES = [
        ('cupon', 'Cupón de Descuento'),
        ('porcentaje', 'Descuento Porcentaje'),
        ('monto', 'Descuento Monto Fijo'),
    ]
    
    texto = models.CharField(max_length=100, verbose_name='Texto del Beneficio')
    tipo_beneficio = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Beneficio')
    cupon = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Cupón Asociado')
    valor_porcentaje = models.IntegerField(null=True, blank=True, verbose_name='Valor Porcentaje (0-100)')
    valor_monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor Monto')
    probabilidad = models.IntegerField(default=10, verbose_name='Probabilidad (1-100)')
    color = models.CharField(max_length=7, default='#E982F2', verbose_name='Color Hexadecimal')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    orden = models.IntegerField(default=0, verbose_name='Orden de visualización')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Beneficio de Ruleta'
        verbose_name_plural = 'Beneficios de Ruleta'
        ordering = ['orden', '-fecha_creacion']
    
    def __str__(self):
        return f'{self.texto} ({self.get_tipo_beneficio_display()})'
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.tipo_beneficio == 'cupon' and not self.cupon:
            raise ValidationError('Debe seleccionar un cupón para tipo "Cupón de Descuento"')
        if self.tipo_beneficio == 'porcentaje' and not self.valor_porcentaje:
            raise ValidationError('Debe especificar el porcentaje de descuento')
        if self.tipo_beneficio == 'monto' and not self.valor_monto:
            raise ValidationError('Debe especificar el monto de descuento')


class UsuarioRuleta(models.Model):
    """Registro de participación de usuarios en la ruleta"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, verbose_name='Usuario')
    ha_girado = models.BooleanField(default=False, verbose_name='Ha Girado')
    beneficio_obtenido = models.ForeignKey(RuletaBeneficio, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Beneficio Obtenido')
    cupon_generado = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='ruleta_cupones', verbose_name='Cupón Generado')
    fecha_giro = models.DateTimeField(null=True, blank=True, verbose_name='Fecha del Giro')
    
    class Meta:
        verbose_name = 'Participación en Ruleta'
        verbose_name_plural = 'Participaciones en Ruleta'
    
    def __str__(self):
        return f'{self.usuario.email} - {"Ha girado" if self.ha_girado else "No ha girado"}'
