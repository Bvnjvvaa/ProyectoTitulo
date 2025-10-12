from django.urls import path
from . import views

urlpatterns = [
    # URLs públicas
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # URLs de verificación de email
    path('verificar-email/<uuid:token>/', views.verificar_email, name='verificar_email'),
    path('reenviar-verificacion/', views.reenviar_email_verificacion, name='reenviar_verificacion'),
    
    # URLs del Panel Admin (solo superusuarios)
    path('panel-admin/usuarios/', views.lista_usuarios_admin, name='lista_usuarios_admin'),
    path('panel-admin/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('panel-admin/usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('panel-admin/usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
