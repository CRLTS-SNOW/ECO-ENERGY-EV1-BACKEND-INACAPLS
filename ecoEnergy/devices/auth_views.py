from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from .models import Organization


def login_view(request):
    """
    Vista de login para empresas.
    Muestra formulario de login y procesa la autenticación.
    """
    if request.user.is_authenticated:
        return redirect('devices:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Por favor, complete todos los campos.')
            return render(request, 'devices/login.html')
        
        # Autenticar usuario
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.first_name or user.email}!')
                return redirect('devices:dashboard')
            else:
                messages.error(request, 'Su cuenta está desactivada.')
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
    
    return render(request, 'devices/login.html')


@login_required
def logout_view(request):
    """
    Vista de logout.
    Cierra la sesión del usuario y redirige al login.
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('devices:login')


def register_view(request):
    """
    Vista de registro para empresas.
    Crea un nuevo usuario y una organización asociada.
    """
    if request.user.is_authenticated:
        return redirect('devices:dashboard')
    
    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validaciones básicas
        if not all([company_name, email, password, password_confirm]):
            messages.error(request, 'Por favor, complete todos los campos.')
            return render(request, 'devices/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'devices/register.html')
        
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'devices/register.html')
        
        # Verificar si el email ya existe
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe una cuenta con este email.')
            return render(request, 'devices/register.html')
        
        try:
            with transaction.atomic():
                # Crear usuario
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=company_name,
                    is_active=True
                )
                
                # Crear organización asociada
                organization = Organization.objects.create(
                    name=company_name
                )
                
                messages.success(request, f'¡Registro exitoso! Bienvenido a Eco Energy, {company_name}.')
                return redirect('devices:login')
                
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Por favor, intente nuevamente.')
            return render(request, 'devices/register.html')
    
    return render(request, 'devices/register.html')


# =========================
# Recuperación de contraseña (HU8)
# =========================
class CustomPasswordResetView(PasswordResetView):
    """
    Vista personalizada para solicitar recuperación de contraseña.
    """
    template_name = 'devices/password_reset.html'
    email_template_name = 'devices/password_reset_email.html'
    subject_template_name = 'devices/password_reset_subject.txt'
    success_url = reverse_lazy('devices:password_reset_done')
    
    def form_valid(self, form):
        """
        Sobrescribir para mostrar mensaje personalizado.
        """
        messages.info(
            self.request, 
            'Si el email existe en nuestro sistema, recibirás instrucciones para recuperar tu contraseña.'
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Vista que confirma el envío del email de recuperación.
    """
    template_name = 'devices/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vista para confirmar la nueva contraseña.
    """
    template_name = 'devices/password_reset_confirm.html'
    success_url = reverse_lazy('devices:password_reset_complete')
    
    def form_valid(self, form):
        """
        Sobrescribir para asegurar que la contraseña se guarde correctamente.
        """
        # Llamar al método padre para guardar la contraseña
        response = super().form_valid(form)
        
        # Agregar mensaje de éxito
        messages.success(
            self.request, 
            '¡Contraseña actualizada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.'
        )
        
        return response


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Vista que confirma el cambio exitoso de contraseña.
    """
    template_name = 'devices/password_reset_complete.html'
