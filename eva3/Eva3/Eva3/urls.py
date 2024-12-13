from django.contrib import admin
from django.urls import path
from Foro import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Home, name='Home'),#   Muestra  la vista index Principal
    path('Perfil/', views.perfil_usuario, name='Perfil'),

    
    path('Login/', views.login_usuario, name='login'),  # Inicio de sesión
    path('Logout/', views.user_logout, name='logout'),  # Cierre de sesión
    path('Registrar/', views.register_usuario, name='registro'),#   Formulario pasa los usuarios

    
    path('tematica/<int:tematica_id>/', views.detalle_tematica, name='detalle_tematica'), 

    # Rutas de Administración 
    path('Admin/', views.admin_panel, name='Admin'), 
    path('Admin/tematicas/', views.gestionar_tematicas, name='gestionar_tematicas'),
    path('Admin/historial/', views.historial_view, name='Historial'),


    path('eliminar_comentario/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
    path('eliminar_usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),



]
