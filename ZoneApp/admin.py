from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Matrona, Servicio, BloqueServicio, disponibilidadServicio, Reservas, Venta, Carrito, CarritoItem, ImagenServicio, Cupon, UsoCupon, Curso, ImagenCurso, InscripcionCurso, OpinionServicio, Anuncio, RuletaBeneficio, UsuarioRuleta


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


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo_descuento', 'valor_descuento', 'usos_actuales', 'usos_maximos', 'activo', 'fecha_expiracion']
    list_filter = ['activo', 'tipo_descuento', 'fecha_inicio', 'fecha_expiracion']
    search_fields = ['codigo', 'descripcion']
    list_editable = ['activo']
    readonly_fields = ['usos_actuales', 'fecha_creacion']
    
    fieldsets = (
        ('Información del Cupón', {
            'fields': ('codigo', 'descripcion', 'activo')
        }),
        ('Descuento', {
            'fields': ('tipo_descuento', 'valor_descuento')
        }),
        ('Restricciones', {
            'fields': ('monto_minimo', 'usos_maximos', 'usos_actuales', 'usos_por_usuario')
        }),
        ('Fechas de Validez', {
            'fields': ('fecha_inicio', 'fecha_expiracion', 'fecha_creacion')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Convertir código a mayúsculas automáticamente
        obj.codigo = obj.codigo.upper()
        super().save_model(request, obj, form, change)


@admin.register(UsoCupon)
class UsoCuponAdmin(admin.ModelAdmin):
    list_display = ['cupon', 'usuario', 'fecha_uso', 'monto_descuento', 'venta']
    list_filter = ['fecha_uso', 'cupon']
    search_fields = ['cupon__codigo', 'usuario__email', 'usuario__first_name']
    readonly_fields = ['fecha_uso']
    date_hierarchy = 'fecha_uso'
    
    fieldsets = (
        ('Información del Uso', {
            'fields': ('cupon', 'usuario', 'venta', 'monto_descuento', 'fecha_uso')
        }),
    )


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'modalidad', 'precio', 'duracion_horas', 'fecha_inicio', 'matrona', 'cupos_ocupados', 'cupos_disponibles', 'activo']
    list_filter = ['modalidad', 'activo', 'fecha_inicio', 'matrona']
    search_fields = ['nombre', 'descripcion', 'matrona__first_name', 'matrona__email']
    list_editable = ['activo']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'matrona')
        }),
        ('Detalles del Curso', {
            'fields': ('precio', 'duracion_horas', 'modalidad', 'cupos_disponibles')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_termino')
        }),
        ('Información Adicional', {
            'fields': ('requisitos', 'contenido', 'ubicacion', 'link_reunion'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
    
    def cupos_ocupados(self, obj):
        return obj.cupos_ocupados
    cupos_ocupados.short_description = 'Inscritos'


@admin.register(ImagenCurso)
class ImagenCursoAdmin(admin.ModelAdmin):
    list_display = ['id', 'curso', 'es_principal']
    list_filter = ['es_principal', 'curso']
    search_fields = ['curso__nombre']
    list_editable = ['es_principal']


@admin.register(InscripcionCurso)
class InscripcionCursoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'curso', 'estado', 'fecha_inscripcion']
    list_filter = ['estado', 'curso', 'fecha_inscripcion']
    search_fields = ['usuario__first_name', 'usuario__email', 'curso__nombre']
    list_editable = ['estado']
    date_hierarchy = 'fecha_inscripcion'
    readonly_fields = ['fecha_inscripcion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información de Inscripción', {
            'fields': ('curso', 'usuario', 'estado')
        }),
        ('Detalles', {
            'fields': ('comentarios', 'fecha_inscripcion', 'fecha_actualizacion')
        }),
    )


@admin.register(OpinionServicio)
class OpinionServicioAdmin(admin.ModelAdmin):
    list_display = ['id', 'servicio', 'usuario', 'calificacion', 'fecha_creacion']
    list_filter = ['calificacion', 'fecha_creacion', 'servicio']
    search_fields = ['usuario__first_name', 'usuario__email', 'servicio__nombre', 'comentario']
    readonly_fields = ['fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información de Opinión', {
            'fields': ('servicio', 'usuario', 'calificacion')
        }),
        ('Contenido', {
            'fields': ('comentario', 'fecha_creacion')
        }),
    )


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ['id', 'texto', 'activo', 'fecha_inicio', 'fecha_fin', 'esta_vigente']
    list_filter = ['activo', 'fecha_inicio', 'fecha_fin']
    search_fields = ['texto']
    list_editable = ['activo']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información del Anuncio', {
            'fields': ('texto', 'enlace', 'texto_enlace')
        }),
        ('Configuración', {
            'fields': ('activo', 'fecha_inicio', 'fecha_fin')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def esta_vigente(self, obj):
        return obj.esta_vigente()
    esta_vigente.boolean = True
    esta_vigente.short_description = 'Vigente'


@admin.register(RuletaBeneficio)
class RuletaBeneficioAdmin(admin.ModelAdmin):
    list_display = ['id', 'texto', 'tipo_beneficio', 'probabilidad', 'color', 'activo', 'orden']
    list_filter = ['activo', 'tipo_beneficio']
    search_fields = ['texto']
    list_editable = ['orden', 'activo', 'probabilidad']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información del Beneficio', {
            'fields': ('texto', 'tipo_beneficio', 'cupon', 'valor_porcentaje', 'valor_monto')
        }),
        ('Configuración de Ruleta', {
            'fields': ('probabilidad', 'color', 'orden', 'activo')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsuarioRuleta)
class UsuarioRuletaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'ha_girado', 'beneficio_obtenido', 'fecha_giro']
    list_filter = ['ha_girado', 'fecha_giro']
    search_fields = ['usuario__email', 'usuario__first_name']
    readonly_fields = ['usuario', 'ha_girado', 'beneficio_obtenido', 'cupon_generado', 'fecha_giro']
