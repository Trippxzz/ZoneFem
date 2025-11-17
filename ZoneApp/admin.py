from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Matrona, Servicio, BloqueServicio, disponibilidadServicio


class MatronaInline(admin.StackedInline):
    model = Matrona
    can_delete = False
    verbose_name_plural = 'Datos de Matrona'
    fields = ('telefono', 'descripcion', 'color_agenda') 


class CustomUsuarioAdmin(BaseUserAdmin):
    inlines = [MatronaInline] 
    
    list_display = ('email', 'first_name', 'rol', 'is_staff')
    search_fields = ('email', 'first_name', 'rut')
    ordering = ('email',) 
    

    add_fieldsets = (
        (None, {
            'classes': ('wide',),

            'fields': ('email', 'first_name', 'rut', 'rol', 'password'), 
        }),
    )


    fieldsets = (
        (None, {'fields': ('email', 'password')}), 
        ('Información Personal', {'fields': ('first_name', 'last_name', 'rut', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    filter_horizontal = ('groups', 'user_permissions',)




@admin.register(BloqueServicio)
class BloqueServicioAdmin(admin.ModelAdmin):
    list_display = ('matrona_display', 'servicio')
    list_filter = ('matrona__first_name', 'servicio__nombre')
    search_fields = ('matrona__email', 'servicio__nombre')
    

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "matrona":
            kwargs["queryset"] = Usuario.objects.filter(rol='matrona')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def matrona_display(self, obj):
        return obj.matrona.get_full_name() or obj.matrona.email
    matrona_display.short_description = 'Matrona Asignada'




@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion')
    search_fields = ('nombre',)
    

try:
    admin.site.unregister(Usuario)
except admin.sites.NotRegistered:
    pass

admin.site.register(Usuario, CustomUsuarioAdmin)