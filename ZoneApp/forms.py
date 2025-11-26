from django import forms
from .models import Usuario, Servicio, BloqueServicio, disponibilidadServicio, Matrona
from django.forms.models import inlineformset_factory
from datetime import date
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmación de contraseña', widget=forms.PasswordInput)
    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'rut', 'fecha_nacimiento', 'telefono']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            }
    def clean(self):
        # Esto verifica que las contraseñas coincidan
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    



class EditarPerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'telefono', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border-2 border-pink-200 rounded-lg focus:outline-none focus:border-pink-400'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border-2 border-pink-200 rounded-lg focus:outline-none focus:border-pink-400'}),
            'email': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border-2 border-pink-200 rounded-lg focus:outline-none focus:border-pink-400'}),
        }
        labels = {
            'first_name': 'Nombre',
            'telefono': 'Teléfono',
            'email': 'Correo:',
        }


class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Correo Electrónico'
        self.fields['username'].widget.attrs['placeholder'] = 'Correo Electrónico'
    
    def clean(self):
        email = self.data.get('username') 
        password = self.data.get('password')

        if email and password:
            self.user_cache = authenticate(request=self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data
    

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion']
        widgets = {
            'descripcion': forms.Textarea(),
        }

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ServicioImagenForm(forms.Form):
    imagenes = forms.ImageField(widget=MultiFileInput(attrs={'multiple': True}), required=False)

disponibilidadServicioFormSet = inlineformset_factory(
    BloqueServicio,
    disponibilidadServicio,
    fields=['dia_semana', 'hora_inicio', 'hora_fin'],
    extra=1,
    can_delete=True
)

class seleccionarServicioForm(forms.Form):
    bloque_servicio = forms.ModelChoiceField(queryset=BloqueServicio.objects.none(), label="Seleccione un Servicio")
    def __init__(self, matrona, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bloque_servicio'].queryset = BloqueServicio.objects.filter(matrona=matrona)





class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100, label='Nombre') 
    email = forms.EmailField(label='Correo Electrónico')
    phone = forms.CharField(max_length=15, required=False, label='Teléfono (Opcional)')
    message = forms.CharField(widget=forms.Textarea, label='Mensaje')

class PerfilMatronaForm(forms.ModelForm):
    # Estos campos son de Usuario
    first_name = forms.CharField(label='Nombre', required=True)
    email = forms.EmailField(label='Correo Electrónico', required=True)
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Matrona
        fields = ['telefono', 'descripcion', 'color_agenda', 'foto_perfil'] 
        labels = {
            'telefono': 'Teléfono',
            'descripcion': 'Biografía Profesional: ',
            'color_agenda': 'Color',
            'foto_perfil': 'Foto de Perfil'
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'color_agenda': forms.TextInput(attrs={'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk and self.instance.usuario:
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['email'].initial = self.instance.usuario.email
            self.fields['fecha_nacimiento'].initial = self.instance.usuario.fecha_nacimiento
    
    def save(self, commit=True):
        # Guardar el perfil de Matrona
        matrona = super().save(commit=False)
        
        # Actualizar datos del Usuario
        usuario = matrona.usuario
        usuario.first_name = self.cleaned_data['first_name']
        usuario.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        
        if commit:
            usuario.save()
            matrona.save()
        
        return matrona