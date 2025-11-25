from django.db.models import Sum
from .models import Carrito, CarritoItem

def cont_carrito(request):
    total_items = 0
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario_id=request.user).first()
        if carrito:
            resultado = CarritoItem.objects.filter(carrito=carrito).aggregate(Sum('cantidad'))
            total_items = resultado['cantidad__sum'] or 0
    return {'total_carrito':total_items}