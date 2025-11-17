# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Matrona

@receiver(post_save, sender=Usuario)
def gestionarpMatrona(sender, instance, **kwargs):
    """
    Se dispara después de guardar un Usuario (cuando el admin cambia el rol).
    Crea, actualiza o elimina el perfil Matrona según el valor del campo 'rol'.
    """
    
    if instance.rol == 'matrona':
        # Crear o actualizar el perfil Matrona
        Matrona.objects.update_or_create(
            usuario=instance,
            defaults={}
        )
        
    # Si el rol NO es 'matrona' (es 'usuario')
    else:
        # Eliminar el perfil Matrona si existe
        try:
            Matrona.objects.get(usuario=instance).delete()
        except Matrona.DoesNotExist:
            pass # No hay perfil Matrona para eliminar