from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Matrona, Servicio, BloqueServicio, disponibilidadServicio, Reservas, Venta, Carrito, CarritoItem, ImagenServicio


class MatronaInline(admin.StackedInline):
    model = Matrona
    can_delete = False
    verbose_name_plural = 'Datos de Matrona'
    fields = ('telefono', 'descripcion', 'color_agenda') 


class CustomUsuarioAdmin(BaseUserAdmin):
    inlines = [MatronaInline] 
    
    list_display = ('email', 'first_name', 'rol', 'is_staff', 'telefono')
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


@admin.register(Reservas)
class ReservasAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'matrona', 'servicio', 'fecha', 'hora_inicio', 'hora_fin', 'estado']
    list_filter = ['estado', 'fecha', 'servicio', 'matrona']
    search_fields = ['usuario__first_name', 'usuario__email', 'matrona__first_name', 'servicio__nombre']
    list_editable = ['estado']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('usuario', 'matrona', 'servicio', 'estado')
        }),
        ('Horario', {
            'fields': ('fecha', 'hora_inicio', 'hora_fin')
        }),
    )
    


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha_venta', 'total_venta', 'estado']
    list_filter = ['fecha_venta']
    readonly_fields = ['fecha_venta']
    # date_hierarchy = 'fecha_venta'
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('fecha_venta',)
        }),
    )

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario']
    search_fields = ['usuario__first_name', 'usuario__email']


@admin.register(CarritoItem)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'carrito']
    list_filter = ['carrito__usuario']
    search_fields = ['carrito__usuario__first_name']
    


@admin.register(ImagenServicio)
class ImagenServicioAdmin(admin.ModelAdmin):
    list_display = ['id', 'servicio', 'es_principal']
    list_filter = ['es_principal', 'servicio']
    search_fields = ['servicio__nombre']
    list_editable = ['es_principal']