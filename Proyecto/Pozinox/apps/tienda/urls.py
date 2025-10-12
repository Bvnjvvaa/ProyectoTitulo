from django.urls import path
from . import views

urlpatterns = [
    # URLs públicas
    path('', views.home, name='home'),
    path('productos/', views.productos_publicos, name='productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
    # URLs del Panel Admin (solo superusuarios)
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-admin/productos/', views.lista_productos_admin, name='lista_productos_admin'),
    path('panel-admin/productos/crear/', views.crear_producto, name='crear_producto'),
    path('panel-admin/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('panel-admin/productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('panel-admin/categorias/', views.lista_categorias_admin, name='lista_categorias_admin'),
    path('panel-admin/categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('panel-admin/categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('panel-admin/categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # URLs de Cotizaciones (usuarios registrados)
    path('cotizaciones/', views.mis_cotizaciones, name='mis_cotizaciones'),
    path('cotizaciones/crear/', views.crear_cotizacion, name='crear_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/', views.detalle_cotizacion, name='detalle_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/agregar-producto/', views.agregar_producto_cotizacion, name='agregar_producto_cotizacion'),
    path('cotizaciones/detalle/<int:detalle_id>/actualizar-cantidad/', views.actualizar_cantidad_producto, name='actualizar_cantidad_producto'),
    path('cotizaciones/detalle/<int:detalle_id>/eliminar/', views.eliminar_producto_cotizacion, name='eliminar_producto_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/finalizar/', views.finalizar_cotizacion, name='finalizar_cotizacion'),
    
    # URLs de Pago
    path('cotizaciones/<int:cotizacion_id>/seleccionar-pago/', views.seleccionar_pago, name='seleccionar_pago'),
    path('cotizaciones/<int:cotizacion_id>/pagar-mercadopago/', views.procesar_pago_mercadopago, name='procesar_pago_mercadopago'),
    path('cotizaciones/<int:cotizacion_id>/pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('cotizaciones/<int:cotizacion_id>/pago-fallido/', views.pago_fallido, name='pago_fallido'),
    path('cotizaciones/<int:cotizacion_id>/pago-pendiente/', views.pago_pendiente, name='pago_pendiente'),
    
    # URLs de descarga PDF
    path('cotizaciones/<int:cotizacion_id>/descargar-pdf/', views.descargar_cotizacion_pdf, name='descargar_cotizacion_pdf'),
]
