from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from .forms import UsuarioForm
from .models import Usuario
# Create your views here.

def home(request):
    return render(request, "index.html")

### ZONE REGISTRO E INICIO DE SESIÓN 
def RegistroUsuarios(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después del registro
            return redirect('home')
    else:
        form = UsuarioForm()
    return render(request, 'ZoneUsuarios/registrousers.html', {'form': form})
        
class LoginView(DjangoLoginView):
    template_name = 'ZoneApp/ZoneUsuarios/login.html'
    success_url = reverse_lazy('home')

