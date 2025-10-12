from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import PerfilUsuario, EmailVerificationToken
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
                # Verificar si el email está verificado (solo si está configurado)
                if getattr(settings, 'EMAIL_VERIFICATION_REQUIRED', False):
                    if not user.perfil.email_verificado:
                        messages.warning(request, 
                            'Debes verificar tu correo electrónico antes de iniciar sesión. '
                            'Revisa tu bandeja de entrada.')
                        return redirect('login')
                
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
            
            # Enviar email de verificación
            if getattr(settings, 'EMAIL_VERIFICATION_REQUIRED', False):
                enviar_email_verificacion(user, request)
                messages.success(request, 
                    '¡Cuenta creada exitosamente! '
                    'Te hemos enviado un correo para verificar tu email. '
                    'Por favor revisa tu bandeja de entrada.')
            else:
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


# ============================================
# SISTEMA DE VERIFICACIÓN DE EMAIL
# ============================================

def enviar_email_verificacion(user, request):
    """Enviar email de verificación a un usuario"""
    # Crear token de verificación
    token = EmailVerificationToken.objects.create(user=user)
    
    # Construir URL de verificación
    verification_url = request.build_absolute_uri(
        f'/usuarios/verificar-email/{token.token}/'
    )
    
    # Renderizar template HTML del email
    html_message = render_to_string('usuarios/email_verificacion.html', {
        'user': user,
        'verification_url': verification_url,
        'expires_hours': 24,
    })
    
    # Crear versión texto plano
    plain_message = strip_tags(html_message)
    
    # Enviar email
    try:
        send_mail(
            subject='Verifica tu correo electrónico - Pozinox',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


def verificar_email(request, token):
    """Vista para verificar el email del usuario"""
    try:
        email_token = EmailVerificationToken.objects.get(token=token)
        
        # Verificar si el token es válido
        if not email_token.is_valid():
            if email_token.is_used:
                messages.info(request, 'Este link de verificación ya ha sido usado.')
            else:
                messages.error(request, 'Este link de verificación ha expirado. Solicita uno nuevo.')
            return redirect('login')
        
        # Marcar email como verificado
        user = email_token.user
        perfil = user.perfil
        perfil.email_verificado = True
        from django.utils import timezone
        perfil.fecha_verificacion_email = timezone.now()
        perfil.save()
        
        # Marcar token como usado
        email_token.mark_as_used()
        
        messages.success(request, 
            '¡Email verificado exitosamente! Ahora puedes iniciar sesión.')
        return redirect('login')
        
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Link de verificación inválido.')
        return redirect('login')


def reenviar_email_verificacion(request):
    """Reenviar email de verificación"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Verificar si ya está verificado
            if user.perfil.email_verificado:
                messages.info(request, 'Este correo ya está verificado.')
                return redirect('login')
            
            # Enviar nuevo email
            if enviar_email_verificacion(user, request):
                messages.success(request, 
                    'Te hemos enviado un nuevo correo de verificación. '
                    'Revisa tu bandeja de entrada.')
            else:
                messages.error(request, 
                    'Hubo un error al enviar el correo. Intenta de nuevo más tarde.')
            
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario con ese correo.')
            return redirect('reenviar_verificacion')
    
    return render(request, 'usuarios/reenviar_verificacion.html')
