# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Matrona

@receiver(post_save, sender=Usuario)
def gestionarpMatrona(sender, instance, created, **kwargs):
    """
    Signal que gestiona la creación/actualización del perfil de matrona
    Se ejecuta cuando:
    1. Se crea un nuevo usuario con rol='matrona'
    2. Se cambia el rol de un usuario existente a 'matrona'
    """
    
    # Si el usuario tiene rol de matrona
    if instance.rol == 'matrona':
        # Intentar obtener o crear el perfil de matrona
        perfil_matrona, perfil_created = Matrona.objects.get_or_create(
            usuario=instance,
            defaults={
                'telefono': instance.telefono if instance.telefono else '',
                'descripcion': '',
                'color_agenda': '#7436ad'
            }
        )
        
        # Si ya existía el perfil, actualizar el teléfono por si cambió
        if not perfil_created and instance.telefono:
            perfil_matrona.telefono = instance.telefono
            perfil_matrona.save(update_fields=['telefono'])
    
    # Si el usuario cambió de matrona a cliente, podríamos eliminar el perfil
    elif instance.rol == 'cliente':
        try:
            perfil_matrona = Matrona.objects.get(usuario=instance)
            # perfil_matrona.delete()  # Descomentar si quieres eliminar
        except Matrona.DoesNotExist:
            pass