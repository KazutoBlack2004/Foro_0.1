from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify

class UsuarioManager(BaseUserManager):
    def create_user(self, rut, correo, nombres, apellido_paterno, apellido_materno, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        usuario = self.model(rut=rut, correo=correo, nombres=nombres, apellido_paterno=apellido_paterno, apellido_materno=apellido_materno, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, rut, correo, nombres, apellido_paterno, apellido_materno, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(rut, correo, nombres, apellido_paterno, apellido_materno, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=9, unique=True)
    nombres = models.CharField(max_length=20)
    apellido_paterno = models.CharField(max_length=20)
    apellido_materno = models.CharField(max_length=20)
    correo = models.EmailField(max_length=50, unique=True)
    nacionalidad = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    estado = models.BooleanField(default=True)  # True = Activo, False = Inactivo
    tematicas = models.ManyToManyField('Tematica', related_name="usuarios", help_text="Temáticas de interés seleccionadas por el usuario.")
    es_admin = models.BooleanField(default=False)  # Indica si el usuario es administrador
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['rut', 'nombres', 'apellido_paterno', 'apellido_materno', 'password']

    objects = UsuarioManager()

    def __str__(self):
        return self.correo




class Tematica(models.Model):
    Tema = models.TextField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    Descripcion = models.TextField(max_length=200, default='Descripción por defecto')
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.Tema)
        super(Tematica, self).save(*args, **kwargs)

    def __str__(self):
        return self.Tema



class Comentario(models.Model):
    comentario = models.TextField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="comentarios")  # Relación con el modelo Usuario
    temati = models.ForeignKey(Tematica, on_delete=models.CASCADE, related_name="comentarios")
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha de creación del comentario

    def clean(self):
        """
        Valida que los usuarios normales no puedan realizar más de 10 comentarios por temática.
        Los administradores están exentos de esta restricción.
        """
        if not self.usuario.es_admin:  # Aplica restricción solo a usuarios normales
            comentarios_usuario = self.usuario.comentarios.filter(temati=self.temati).count()
            if comentarios_usuario >= 10:
                raise ValidationError(
                    f"Solo puedes realizar hasta 10 comentarios en la temática '{self.temati}'."
                )

    def save(self, *args, **kwargs):
        # Llama al método clean antes de guardar
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.temati} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"


class Historial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion_historial = models.TextField(max_length=200)
    tabla_afectada_historial = models.TextField(max_length=100)
    fecha_hora_historial = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.usuario} - {self.descripcion_historial} - "
            f"{self.tabla_afectada_historial} - {self.fecha_hora_historial}"
        )



def historial_view(request): 
    historial = Historial.objects.all().order_by('-fecha_hora_historial') # Ordenar por fecha, del más reciente al más antiguo 
    return render(request, 'historial.html', {'historial': historial})