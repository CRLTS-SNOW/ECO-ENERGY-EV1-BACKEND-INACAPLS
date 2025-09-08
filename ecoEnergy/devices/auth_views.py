from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

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
