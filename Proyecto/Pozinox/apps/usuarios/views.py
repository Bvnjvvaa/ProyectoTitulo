from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import PerfilUsuario
from .forms import LoginForm, RegistroForm


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
