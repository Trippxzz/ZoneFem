from django import forms
from .models import Usuario
from datetime import date

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmación de contraseña', widget=forms.PasswordInput)
    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'rut']
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