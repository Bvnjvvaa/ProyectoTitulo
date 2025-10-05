from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Agregar más URLs aquí según necesites
    # path('productos/', views.productos, name='productos'),
    # path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
    # path('categoria/<int:id>/', views.categoria, name='categoria'),
]
