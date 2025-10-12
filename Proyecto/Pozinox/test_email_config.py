"""
Script para probar la configuración de email de Gmail
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pozinox.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("VERIFICACIÓN DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)
print()
print(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"🔒 EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)} ({len(settings.EMAIL_HOST_PASSWORD)} caracteres)")
print()
print("=" * 60)
print()

# Intentar enviar email de prueba
print("📨 Intentando enviar email de prueba...")
print()

try:
    resultado = send_mail(
        subject='🧪 Prueba de Configuración - Pozinox',
        message='Este es un email de prueba para verificar que la configuración funciona correctamente.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],  # Enviarte a ti mismo
        fail_silently=False,
    )
    
    print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
    print(f"📬 Revisa la bandeja de entrada de: {settings.EMAIL_HOST_USER}")
    print()
    print("=" * 60)
    print()
    print("🎉 La configuración es correcta. El sistema de verificación de email funcionará.")
    print()
    
except Exception as e:
    print("❌ ERROR AL ENVIAR EMAIL")
    print()
    print(f"Tipo de error: {type(e).__name__}")
    print(f"Mensaje: {e}")
    print()
    print("=" * 60)
    print()
    print("🔍 POSIBLES CAUSAS:")
    print()
    print("1. ❌ La App Password es incorrecta")
    print("   Solución: Genera una nueva en https://myaccount.google.com/apppasswords")
    print()
    print("2. ❌ No tienes Verificación en 2 pasos activada")
    print("   Solución: Actívala en https://myaccount.google.com/security")
    print()
    print("3. ❌ La App Password es de otra cuenta de Gmail")
    print("   Solución: Asegúrate de estar con pozinox.empresa@gmail.com al generarla")
    print()
    print("4. ❌ Hay espacios en la App Password")
    print("   Solución: Copia la password SIN espacios (ejemplo: abcdefghijklmnop)")
    print()
    print("=" * 60)
    print()
    print("💡 RECOMENDACIÓN:")
    print()
    print("   1. Ve a https://myaccount.google.com/apppasswords")
    print("   2. Inicia sesión con: pozinox.empresa@gmail.com")
    print("   3. Genera una NUEVA App Password")
    print("   4. Cópiala SIN espacios")
    print("   5. Pégala en settings.py")
    print()

