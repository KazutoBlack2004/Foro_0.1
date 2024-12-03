from Foro.models import Usuario, Comentario, Tematica, Historial
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # Para mostrar mensajes
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password  # Para verificar la contraseña de manera segura
from .forms import RegistroForms, LoginForms, PerfilForm, UsuarioCreationForm, TematicaForm
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone




# Lista de palabras groseras (puedes expandir esta lista según sea necesario)
PALABRAS_PROHIBIDAS = [
    "puta", "puto", "mierda", "carajo", "estúpido", "idiota", "imbécil", 
    "cabrón", "gilipollas", "pendejo", "joder", "coño", "zorra", "cabrona", 
    "maldito", "bastardo", "culero", "chingar", "chingado", "chingón", 
    "verga", "pija", "hijo de puta", "tonto", "tarado", "pelotudo", 
    "boludo", "maricón", "gay", "lesbiana", "homosexual", "negro", 
    "feo", "manco", "loco", "sádico", "sapo", "baboso", "vaca", 
    "infeliz", "gorda", "estúpida", "tonta", "pajero", "mamón", 
    "naco", "pendeja", "putona", "chinga tu madre", "vete a la mierda", 
    "huevón", "parásito", "retardado",
    "zángano", "cerda", "babosa", "gil", "subnormal", "desgraciado", 
    "tarada", "rata", "puerca", "muerta de hambre", "narco", "racista", 
    "analfabeta", "estafador", "fascista", 
    "inútil", "patán",
    "basura",
    "prostituta", "alcahueta",
    "engañador", "abusador", "tarado"
]

# Vista del panel de administración
def admin_panel(request):

    return render(request, 'Admin.html')

def Home(request):
    if request.user.is_authenticated:
        tematicas = request.user.tematicas.all()  # Temáticas seleccionadas por el usuario
    else:
        tematicas = Tematica.objects.none()  # No hay temáticas para usuarios anónimos
    
    contexto = {
        'tematicas': tematicas
    }

    return render(request, 'Home.html', contexto)


def Registration(request):

    return render(request, 'Registration.html')

def perfil_usuario(request):
    usuario = request.user
    if request.method == 'POST':
        if 'eliminar_cuenta' in request.POST:
            # Registro en el historial
            Historial.objects.create(
                usuario=request.user,
                descripcion_historial=f"Eliminó su cuenta de usuario",
                tabla_afectada_historial="Usuario",
                fecha_hora_historial=timezone.now()
            )
            usuario.delete()
            logout(request)
            return redirect('Home')
        else:
            form = PerfilForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                # Registro en el historial
                Historial.objects.create(
                    usuario=request.user,
                    descripcion_historial=f"Actualizó su perfil",
                    tabla_afectada_historial="Usuario",
                    fecha_hora_historial=timezone.now()
                )
                return redirect('Perfil')
    else:
        form = PerfilForm(instance=usuario)
    
    contexto = {
        'form': form,
        'usuario': usuario
    }
    return render(request, 'Perfil.html', contexto)


###########################################################################
###########################################################################

# Función para registrar , cerrar seccion y login no modificar esta correcto!! 


def user_logout(request):
    # Registro en el historial
    if request.user.is_authenticated:  # Solo registrar si el usuario está autenticado
        Historial.objects.create(
            usuario=request.user,
            descripcion_historial="Cerró sesión",
            tabla_afectada_historial="Usuario",
            fecha_hora_historial=timezone.now()
        )

    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('Home')  # Redirige al index después del cierre de sesión

def register_usuario(request):
    if request.method == "POST":
        form = RegistroForms(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data.get('password'))
            usuario.save()
            # Registro en el historial
            Historial.objects.create(
                usuario=usuario,
                descripcion_historial="Se registró como nuevo usuario",
                tabla_afectada_historial="Usuario",
                fecha_hora_historial=timezone.now()
            )
            backend = 'Foro.backends.CorreoBackend'
            usuario.backend = backend
            login(request, usuario, backend=backend)
            return redirect('Home')
    else:
        form = RegistroForms()
    return render(request, 'Registration.html', {'form': form})

def login_usuario(request):
    if request.method == "POST":
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')
        usuario = authenticate(request, username=correo, password=contraseña)
        if usuario is not None:
            login(request, usuario)
            # Registro en el historial
            Historial.objects.create(
                usuario=usuario,
                descripcion_historial="Inició sesión",
                tabla_afectada_historial="Usuario",
                fecha_hora_historial=timezone.now()
            )
            return redirect('Home')
        else:
            return redirect('Home')
    return render(request, 'Registration.html')


###########################################################################
###########################################################################

def detalle_tematica(request, tematica_id):
    tematica = get_object_or_404(Tematica, id=tematica_id)
    comentarios = Comentario.objects.filter(temati=tematica)

    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if any(palabra in contenido.lower() for palabra in PALABRAS_PROHIBIDAS):
            messages.error(request, "Tu comentario contiene palabras inapropiadas.")
        else:
            comentarios = Comentario.objects.create(
                usuario=request.user,
                temati=tematica,
                comentario=contenido
            )
            # Registro en el historial
            Historial.objects.create(
                usuario=request.user,
                descripcion_historial=f"Comentó en la temática '{tematica.Tema}'",
                tabla_afectada_historial="Comentario",
                fecha_hora_historial=timezone.now()
            )
            return redirect('detalle_tematica', tematica_id=tematica.id)

    contexto = {
        'tematica': tematica,
        'comentarios': comentarios,
    }

    return render(request, 'DetalleTematica.html', contexto)


# Vista para gestionar temáticas
def gestionar_tematicas(request):
    tematicas = Tematica.objects.all()

    if request.method == 'POST':
        if 'crear' in request.POST:
            form = TematicaForm(request.POST)
            if form.is_valid():
                tematica = form.save()
                # Registro en el historial
                Historial.objects.create(
                    usuario=request.user,
                    descripcion_historial=f"Creó la temática '{tematica.Tema}'",
                    tabla_afectada_historial="Temática",
                    fecha_hora_historial=timezone.now()
                )
                return redirect('gestionar_tematicas')
        elif 'editar' in request.POST:
            tematica_id = request.POST.get('tematica_id')
            tematica = get_object_or_404(Tematica, id=tematica_id)
            form = TematicaForm(request.POST, instance=tematica)
            if form.is_valid():
                form.save()
                # Registro en el historial
                Historial.objects.create(
                    usuario=request.user,
                    descripcion_historial=f"Editó la temática '{tematica.Tema}'",
                    tabla_afectada_historial="Temática",
                    fecha_hora_historial=timezone.now()
                )
                return redirect('gestionar_tematicas')
        elif 'eliminar' in request.POST:
            tematica_id = request.POST.get('tematica_id')
            tematica = get_object_or_404(Tematica, id=tematica_id)
            tematica.delete()
            # Registro en el historial
            Historial.objects.create(
                usuario=request.user,
                descripcion_historial=f"Eliminó la temática con ID {tematica_id}",
                tabla_afectada_historial="Temática",
                fecha_hora_historial=timezone.now()
            )
            return redirect('gestionar_tematicas')
    else:
        form = TematicaForm()

    contexto = {
        'tematicas': tematicas,
        'form': form,
    }
    return render(request, 'GestionTematicas.html', contexto)

@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    if request.user.is_superuser or request.user.es_admin:
        comentario.delete()
        # Crear un registro en el historial
        Historial.objects.create(
            usuario=request.user,
            descripcion_historial=f"Eliminó el comentario con ID {comentario_id}",
            tabla_afectada_historial="Comentario",
            fecha_hora_historial=timezone.now()
        )
        messages.success(request, 'El comentario ha sido eliminado.')
    else:
        messages.error(request, 'No tienes permisos para eliminar este comentario.')
    return redirect(request.META.get('HTTP_REFERER', 'nombre_de_la_vista'))

@login_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.user == usuario:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
    elif request.user.is_superuser or request.user.es_admin:
        usuario.delete()
                # Crear un registro en el historial
        Historial.objects.create(
            usuario=request.user,
            descripcion_historial=f"Eliminó el usuario con ID {comentario_id}",
            tabla_afectada_historial="Usuarios",
            fecha_hora_historial=timezone.now()
        )
        messages.success(request, 'El usuario ha sido eliminado.')
    else:
        messages.error(request, 'No tienes permisos para eliminar este usuario.')
    return redirect(request.META.get('HTTP_REFERER', 'nombre_de_la_vista'))


@staff_member_required
def historial_view(request): 
    historial = Historial.objects.all().order_by('-fecha_hora_historial')
    return render(request, 'historial.html', {'historial': historial})
