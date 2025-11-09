from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager, Group, Permission
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