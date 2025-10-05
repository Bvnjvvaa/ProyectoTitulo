from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import Producto, CategoriaAcero
from .forms import ProductoForm, CategoriaForm


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


def productos_publicos(request):
    """Vista pública de productos para todos los usuarios"""
    productos = Producto.objects.filter(activo=True)
    categorias = CategoriaAcero.objects.filter(activa=True)
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(codigo_producto__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page')
    productos_paginados = paginator.get_page(page_number)
    
    context = {
        'productos': productos_paginados,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'busqueda': busqueda,
    }
    return render(request, 'tienda/productos.html', context)


def detalle_producto(request, producto_id):
    """Vista de detalle de un producto específico"""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    
    # Productos relacionados (misma categoría)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'tienda/detalle_producto.html', context)


# Decorador para verificar si es superusuario
def es_superusuario(user):
    return user.is_superuser


@login_required
@user_passes_test(es_superusuario)
def panel_admin(request):
    """Panel de administración para superusuarios"""
    context = {
        'total_productos': Producto.objects.count(),
        'productos_activos': Producto.objects.filter(activo=True).count(),
        'productos_stock_bajo': Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count(),
        'total_categorias': CategoriaAcero.objects.count(),
    }
    return render(request, 'tienda/panel_admin.html', context)


@login_required
@user_passes_test(es_superusuario)
def lista_productos_admin(request):
    """Lista de productos para administración"""
    productos = Producto.objects.all().order_by('-fecha_creacion')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    estado = request.GET.get('estado')
    busqueda = request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado == 'activos':
        productos = productos.filter(activo=True)
    elif estado == 'inactivos':
        productos = productos.filter(activo=False)
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(codigo_producto__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(productos, 20)
    page_number = request.GET.get('page')
    productos_paginados = paginator.get_page(page_number)
    
    categorias = CategoriaAcero.objects.all()
    
    context = {
        'productos': productos_paginados,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'estado_actual': estado,
        'busqueda': busqueda,
    }
    return render(request, 'tienda/admin/lista_productos.html', context)


@login_required
@user_passes_test(es_superusuario)
def crear_producto(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('lista_productos_admin')
    else:
        form = ProductoForm()
    
    context = {'form': form, 'titulo': 'Crear Producto'}
    return render(request, 'tienda/admin/formulario_producto.html', context)


@login_required
@user_passes_test(es_superusuario)
def editar_producto(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('lista_productos_admin')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form, 
        'producto': producto,
        'titulo': 'Editar Producto'
    }
    return render(request, 'tienda/admin/formulario_producto.html', context)


@login_required
@user_passes_test(es_superusuario)
def eliminar_producto(request, producto_id):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('lista_productos_admin')
    
    context = {'producto': producto}
    return render(request, 'tienda/admin/confirmar_eliminar.html', context)


@login_required
@user_passes_test(es_superusuario)
def lista_categorias_admin(request):
    """Lista de categorías para administración"""
    categorias = CategoriaAcero.objects.all().order_by('nombre')
    
    # Filtros
    estado = request.GET.get('estado')
    busqueda = request.GET.get('q')
    
    if estado == 'activas':
        categorias = categorias.filter(activa=True)
    elif estado == 'inactivas':
        categorias = categorias.filter(activa=False)
    
    if busqueda:
        categorias = categorias.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(categorias, 20)
    page_number = request.GET.get('page')
    categorias_paginadas = paginator.get_page(page_number)
    
    context = {
        'categorias': categorias_paginadas,
        'estado_actual': estado,
        'busqueda': busqueda,
    }
    return render(request, 'tienda/admin/lista_categorias.html', context)


@login_required
@user_passes_test(es_superusuario)
def crear_categoria(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('lista_categorias_admin')
    else:
        form = CategoriaForm()
    
    context = {'form': form, 'titulo': 'Crear Categoría'}
    return render(request, 'tienda/admin/formulario_categoria.html', context)


@login_required
@user_passes_test(es_superusuario)
def editar_categoria(request, categoria_id):
    """Editar categoría existente"""
    categoria = get_object_or_404(CategoriaAcero, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente.')
            return redirect('lista_categorias_admin')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form, 
        'categoria': categoria,
        'titulo': 'Editar Categoría'
    }
    return render(request, 'tienda/admin/formulario_categoria.html', context)


@login_required
@user_passes_test(es_superusuario)
def eliminar_categoria(request, categoria_id):
    """Eliminar categoría"""
    categoria = get_object_or_404(CategoriaAcero, id=categoria_id)
    
    # Verificar si hay productos asociados
    productos_asociados = Producto.objects.filter(categoria=categoria).count()
    
    if request.method == 'POST':
        nombre_categoria = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente.')
        return redirect('lista_categorias_admin')
    
    context = {
        'categoria': categoria,
        'productos_asociados': productos_asociados
    }
    return render(request, 'tienda/admin/confirmar_eliminar_categoria.html', context)
