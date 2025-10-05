from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto, CategoriaAcero


def home(request):
    """Vista principal de la página de inicio"""
    # Obtener productos destacados
    productos_destacados = Producto.objects.filter(activo=True)[:6]
    
    # Obtener categorías principales
    categorias = CategoriaAcero.objects.filter(activa=True)[:4]
    
    context = {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'titulo': 'Pozinox - Tienda de Aceros',
    }
    return render(request, 'tienda/home.html', context)
