from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Usuario, Tematica

class LoginForms(forms.Form):
    gmail = forms.EmailField(label="Correo electrónico", max_length=250)
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

class RegistroForms(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Usuario 
        fields = [
            'rut', 'nombres', 'apellido_paterno', 'apellido_materno', 
            'password', 'correo', 'nacionalidad', 'tematicas'
        ]
    tematicas = forms.ModelMultipleChoiceField(
        queryset=Tematica.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tematica-buttons'}))

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario

class UsuarioCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = [
            'rut', 'correo', 'nombres', 'apellido_paterno', 
            'apellido_materno', 'nacionalidad', 'tematicas', 'es_admin'
        ]
        tematicas = forms.ModelMultipleChoiceField(
        queryset=Tematica.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tematica-buttons'}))

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario


class UsuarioChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Usuario
        fields = [
            'correo', 'password', 'is_active', 'is_staff', 
            'is_superuser', 'groups', 'user_permissions'
        ]
    tematicas = forms.ModelMultipleChoiceField(
        queryset=Tematica.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tematica-buttons'}))

    def clean_password(self):
        return self.initial["password"]

class PerfilForm(forms.ModelForm):
    tematicas = forms.ModelMultipleChoiceField(
        queryset=Tematica.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tematica-buttons'}))

    class Meta:
        model = Usuario
        fields = ['rut', 'nombres', 'apellido_paterno', 'apellido_materno', 'correo', 'nacionalidad', 'tematicas']



    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class TematicaForm(forms.ModelForm):
    class Meta:
        model = Tematica
        fields = ['Tema', 'slug', 'Descripcion']

