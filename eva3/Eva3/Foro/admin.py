from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Tematica, Comentario, Historial
from .forms import UsuarioCreationForm, UsuarioChangeForm

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm

    list_display = (
        'rut', 
        'nombres', 
        'apellido_paterno', 
        'apellido_materno', 
        'correo', 
        'nacionalidad', 
        'estado', 
        'es_admin'
    )
    search_fields = (
        'rut', 
        'nombres', 
        'apellido_paterno', 
        'correo', 
        'nacionalidad'
    )
    list_filter = (
        'estado', 
        'es_admin', 
        'nacionalidad'
    )
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'rut', 
                'nombres', 
                'apellido_paterno', 
                'apellido_materno', 
                'correo', 
                'password',  # Asegúrate de usar 'password'
                'nacionalidad'
            )
        }),
        ('Permisos y Estado', {
            'fields': (
                'es_admin', 
                'estado', 
                'tematicas'
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    filter_horizontal = ('tematicas',)
    ordering = ('correo',)

# Registro del modelo Tematica
@admin.register(Tematica)
class TematicaAdmin(admin.ModelAdmin):
    list_display = ('Tema', 'Descripcion', 'created_on')  # Mostrar el tema, descripción y la fecha de creación
    search_fields = ('Tema', 'Descripcion')  # Permitir buscar por tema y descripción
    list_filter = ('Tema', 'created_on')  # Filtrar por tema y fecha de creación

    prepopulated_fields = {'slug': ('Tema',)}  # Prepopula el campo slug basado en el tema


# Registro del modelo Comentario
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'comentario', 'fecha')  # Cambiar 'contenido' por 'comentario' y 'fecha_creacion' por 'fecha'
    search_fields = ('usuario__correo', 'comentario')  # Buscar por 'correo' del usuario y 'comentario'
    list_filter = ('fecha',)  # Filtrar por 'fecha'
    fields = ('usuario', 'comentario', 'temati')  # Solo los campos 'usuario', 'comentario' y 'temati'

# Registro del modelo Historial
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'descripcion_historial', 'tabla_afectada_historial', 'fecha_hora_historial')  # Usar los campos correctos
    search_fields = ('usuario__correo', 'descripcion_historial', 'tabla_afectada_historial')  # Buscar por 'correo' del usuario y los otros campos
    list_filter = ('fecha_hora_historial', 'tabla_afectada_historial')  # Filtrar por 'fecha_hora_historial' y 'tabla_afectada_historial'
    date_hierarchy = 'fecha_hora_historial'  # Permite un filtro jerárquico por fecha

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('usuario')
