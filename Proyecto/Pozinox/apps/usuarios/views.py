from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
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
    """Vista para el registro en una sola página"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # Verificar que el email no esté registrado
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe una cuenta con ese correo electrónico.')
                return render(request, 'usuarios/registro.html', {'form': form})
            
            # Verificar que el email esté verificado
            if request.session.get('email_verificado') != email:
                messages.error(request, 'Debes verificar tu correo electrónico antes de completar el registro.')
                return render(request, 'usuarios/registro.html', {'form': form})
            
            # Crear usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=email,
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
            )
            
            # Actualizar perfil
            perfil = user.perfil
            perfil.tipo_usuario = 'cliente'  # Todos los usuarios son clientes
            perfil.telefono = form.cleaned_data.get('telefono', '')
            perfil.direccion = form.cleaned_data.get('direccion', '')
            perfil.comuna = form.cleaned_data.get('comuna', '')
            perfil.ciudad = form.cleaned_data.get('ciudad', '')
            perfil.email_verificado = True  # Ya verificado
            perfil.fecha_verificacion_email = timezone.now()
            perfil.save()
            
            # Limpiar sesión
            if 'email_verificado' in request.session:
                del request.session['email_verificado']
            
            messages.success(request, 
                '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.')
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

def enviar_codigo_verificacion(email, codigo):
    """Enviar código de 6 dígitos al email"""
    # Renderizar template HTML del email
    html_message = render_to_string('usuarios/email_codigo_verificacion.html', {
        'email': email,
        'codigo': codigo,
        'expires_minutes': 10,
    })
    
    # Crear versión texto plano
    plain_message = f"""
Hola,

Tu código de verificación para Pozinox es: {codigo}

Este código es válido por 10 minutos.

Si no solicitaste este código, puedes ignorar este mensaje.

Saludos,
Equipo Pozinox
    """
    
    # Enviar email
    try:
        send_mail(
            subject='Tu código de verificación - Pozinox',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


def enviar_codigo_verificacion_ajax(request):
    """Enviar código de verificación via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email requerido'})
        
        # Verificar que el email no esté registrado
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Ya existe una cuenta con ese correo electrónico.'})
        
        # Invalidar códigos anteriores
        EmailVerificationToken.objects.filter(
            email=email,
            is_used=False
        ).update(is_used=True)
        
        # Generar nuevo código
        codigo_token = EmailVerificationToken.objects.create(email=email)
        
        # Enviar email
        if enviar_codigo_verificacion(email, codigo_token.codigo):
            return JsonResponse({
                'success': True, 
                'message': f'Código enviado a {email}',
                'codigo': codigo_token.codigo  # Para testing, remover en producción
            })
        else:
            return JsonResponse({'success': False, 'message': 'Error al enviar el código'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


def verificar_codigo_ajax(request):
    """Verificar código via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.POST.get('email')
        codigo = request.POST.get('codigo')
        
        if not email or not codigo:
            return JsonResponse({'success': False, 'message': 'Email y código requeridos'})
        
        # Buscar el código más reciente para este email
        try:
            codigo_token = EmailVerificationToken.objects.filter(
                email=email,
                is_used=False
            ).latest('created_at')
            
            # Verificar el código
            if codigo_token.verificar_codigo(codigo):
                # Código correcto - Marcar como verificado en sesión
                request.session['email_verificado'] = email
                
                return JsonResponse({
                    'success': True, 
                    'message': '¡Email verificado exitosamente! Ahora puedes completar tu registro.',
                })
            else:
                # Código incorrecto
                if codigo_token.intentos >= 5:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Máximo de intentos alcanzado. Solicita un nuevo código.'
                    })
                
                return JsonResponse({
                    'success': False, 
                    'message': f'Código incorrecto. Te quedan {5 - codigo_token.intentos} intentos.'
                })
                
        except EmailVerificationToken.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Código expirado o inválido'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


# ============================================
# API PARA CHATBOT - TOKENS
# ============================================

@login_required
def api_generate_token(request):
    """Generar token de API para chatbot"""
    if request.method == 'POST':
        try:
            perfil = request.user.perfil
            token = perfil.generate_api_token()
            
            return JsonResponse({
                'success': True,
                'token': token,
                'message': 'Token generado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al generar token: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


def api_validate_token(request):
    """Validar token de API para chatbot"""
    if request.method == 'POST':
        token = request.POST.get('token')
        
        if not token:
            return JsonResponse({
                'success': False,
                'message': 'Token requerido'
            })
        
        try:
            perfil = PerfilUsuario.objects.get(api_token=token)
            
            # Verificar que el token no esté expirado (válido por 30 días)
            from datetime import timedelta
            if perfil.token_created and perfil.token_created + timedelta(days=30) > timezone.now():
                return JsonResponse({
                    'success': True,
                    'valid': True,
                    'user_id': perfil.user.id,
                    'username': perfil.user.username,
                    'tipo_usuario': perfil.tipo_usuario,
                    'message': 'Token válido'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'valid': False,
                    'message': 'Token expirado'
                })
        except PerfilUsuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'valid': False,
                'message': 'Token inválido'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al validar token: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def api_revoke_token(request):
    """Revocar token de API"""
    if request.method == 'POST':
        try:
            perfil = request.user.perfil
            perfil.revoke_api_token()
            
            return JsonResponse({
                'success': True,
                'message': 'Token revocado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al revocar token: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


