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
]
