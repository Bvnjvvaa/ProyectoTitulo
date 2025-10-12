from django.contrib import admin
from .models import PerfilUsuario, ConfiguracionSistema, LogActividad, Notificacion, EmailVerificationToken


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipo_usuario', 'email_verificado', 'telefono', 'activo']
    list_filter = ['tipo_usuario', 'email_verificado', 'activo']
    search_fields = ['user__username', 'user__email', 'telefono']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'fecha_verificacion_email']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created_at', 'used_at']


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('nombre_empresa', 'rut_empresa', 'direccion_empresa', 'telefono_empresa', 'email_empresa')
        }),
        ('Configuraciones de Inventario', {
            'fields': ('stock_minimo_global', 'alerta_stock_bajo', 'alerta_stock_critico')
        }),
        ('Configuraciones de Pedidos', {
            'fields': ('iva_porcentaje', 'dias_entrega_default')
        }),
        ('Interfaz', {
            'fields': ('logo_empresa', 'color_primario', 'color_secundario')
        }),
    )


@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_actividad', 'descripcion', 'fecha_actividad']
    list_filter = ['tipo_actividad', 'fecha_actividad']
    search_fields = ['usuario__username', 'descripcion']
    readonly_fields = ['fecha_actividad']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'titulo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida', 'fecha_creacion']
    search_fields = ['usuario__username', 'titulo', 'mensaje']
    readonly_fields = ['fecha_creacion', 'fecha_leida']
