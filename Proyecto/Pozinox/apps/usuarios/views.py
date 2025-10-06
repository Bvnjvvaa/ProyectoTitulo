from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import PerfilUsuario
from .forms import LoginForm, RegistroForm, UsuarioForm


def login_view(request):
    """Vista para el login de usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.first_name or user.username}!')
                
                # Redirigir al next si existe, sino al home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def registro_view(request):
    """Vista para el registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear perfil de usuario
            perfil = user.perfil
            perfil.tipo_usuario = form.cleaned_data['tipo_usuario']
            perfil.telefono = form.cleaned_data['telefono']
            perfil.direccion = form.cleaned_data['direccion']
            perfil.comuna = form.cleaned_data['comuna']
            perfil.ciudad = form.cleaned_data['ciudad']
            perfil.save()
            
            messages.success(request, '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def logout_view(request):
    """Vista para cerrar sesión"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f'Hasta luego, {username}.')
    
    return redirect('home')


@login_required
def perfil_view(request):
    """Vista para mostrar el perfil del usuario"""
    return render(request, 'usuarios/perfil.html', {'user': request.user})


# Decorador para verificar si es superusuario
def es_superusuario(user):
    return user.is_superuser


@login_required
@user_passes_test(es_superusuario)
def lista_usuarios_admin(request):
    """Lista de usuarios para administración"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    usuarios = User.objects.all().order_by('-date_joined')
    
    # Filtros
    tipo_usuario = request.GET.get('tipo')
    estado = request.GET.get('estado')
    busqueda = request.GET.get('q')
    
    if tipo_usuario:
        usuarios = usuarios.filter(perfil__tipo_usuario=tipo_usuario)
    
    if estado == 'activos':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'inactivos':
        usuarios = usuarios.filter(is_active=False)
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    usuarios_paginados = paginator.get_page(page_number)
    
    context = {
        'usuarios': usuarios_paginados,
        'tipo_actual': tipo_usuario,
        'estado_actual': estado,
        'busqueda': busqueda,
        'tipos_usuario': PerfilUsuario.TIPO_USUARIO,
    }
    return render(request, 'usuarios/admin/lista_usuarios.html', context)


@login_required
@user_passes_test(es_superusuario)
def crear_usuario(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.username}" creado exitosamente.')
            return redirect('lista_usuarios_admin')
    else:
        form = UsuarioForm()
    
    context = {'form': form, 'titulo': 'Crear Usuario'}
    return render(request, 'usuarios/admin/formulario_usuario.html', context)


@login_required
@user_passes_test(es_superusuario)
def editar_usuario(request, usuario_id):
    """Editar usuario existente"""
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado exitosamente.')
            return redirect('lista_usuarios_admin')
    else:
        form = UsuarioForm(instance=usuario)
    
    context = {
        'form': form, 
        'usuario': usuario,
        'titulo': 'Editar Usuario'
    }
    return render(request, 'usuarios/admin/formulario_usuario.html', context)


@login_required
@user_passes_test(es_superusuario)
def eliminar_usuario(request, usuario_id):
    """Eliminar usuario"""
    usuario = get_object_or_404(User, id=usuario_id)
    
    # No permitir eliminar el propio usuario
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('lista_usuarios_admin')
    
    if request.method == 'POST':
        nombre_usuario = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{nombre_usuario}" eliminado exitosamente.')
        return redirect('lista_usuarios_admin')
    
    context = {'usuario': usuario}
    return render(request, 'usuarios/admin/confirmar_eliminar_usuario.html', context)
