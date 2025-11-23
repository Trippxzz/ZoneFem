from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager, Group, Permission
from django.utils import timezone
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
    USERNAME_FIELD = 'email' # Para que se pida el correo para iniciar sesión
    REQUIRED_FIELDS = ['first_name', 'rut']
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
    

class Matrona(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_matrona', verbose_name='Usuario Matrona')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono de Contacto')
    descripcion = models.TextField(verbose_name='Descripción/Especialidad', blank=True)
    color_agenda = models.CharField(
            max_length=7, 
            default="#7436ad", 
            verbose_name='Color en Agenda'
        )
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

    def __str__(self):
        return self.nombre
    def imagen_principal(self):
        return self.imagenes.filter(es_principal=True).first()

class ImagenServicio(models.Model):
    servicio = models.ForeignKey(Servicio, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='servicios/')
    es_principal = models.BooleanField(default=False, verbose_name='¿Imagen Principal?')

    def __str__(self):
        return f"Imagen de {self.servicio.nombre}"
    
    def save(self, *args, **kwargs):
        if self.es_principal:
            ImagenServicio.objects.filter(servicio=self.servicio, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)


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
        return f"Reserva de {self.servicio.nombre} por {self.usuario.nombre} el {self.fecha} a las {self.hora_inicio}"
    
class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.email}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='carrito_items')
    cantidad= models.PositiveIntegerField(default=1, editable=False)
    def __str__(self):
        return f"{self.cantidad} x {self.servicio.nombre} en el carrito de {self.carrito.id}"
    @property
    def subtotal(self):
        return self.servicio.precio * self.cantidad


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