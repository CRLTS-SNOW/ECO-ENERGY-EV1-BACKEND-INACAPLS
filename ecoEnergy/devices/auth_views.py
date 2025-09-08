from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse


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
