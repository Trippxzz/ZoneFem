from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Usuario
# Register your models here.

class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'rol', 'is_staff')
    search_fields = ('email', 'first_name', 'rut')

    ordering = ('email',) 
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # Se usa 'email' en lugar de 'username'
        ('Información Personal', {'fields': ('first_name', 'last_name', 'rut', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'rol'), 
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)