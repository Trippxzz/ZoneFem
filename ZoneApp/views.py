from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .forms import UsuarioForm, EmailAuthenticationForm
from .models import Usuario
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.

def home(request):
    loginf = EmailAuthenticationForm()
    return render(request, "index.html", {'loginf': loginf})

### ZONE REGISTRO E INICIO DE SESIÓN 
def RegistroUsuarios(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password')
            user_auth = authenticate(request, email=user.email, password=raw_password)
            if user_auth is not None:
                login(request, user_auth)  # Inicia sesión automáticamente después del registro
            return redirect('home')
    else:
        form = UsuarioForm()
    return render(request, 'ZoneUsuarios/registrousers.html', {'form': form})

@require_POST       
def login_ajax(request):
    form = EmailAuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return JsonResponse({'success': True, 'redirect_url': reverse_lazy('home')})
    return JsonResponse({'success': False, 'errors': form.errors})

