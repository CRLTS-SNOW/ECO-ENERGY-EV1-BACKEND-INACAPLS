# ecoEnergy/devices/urls.py
from django.urls import path
from .views import dashboard, device_list, device_detail, measurement_list, alert_list
from .auth_views import (
    login_view, logout_view, register_view,
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)

app_name = "devices"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("login/", login_view, name="login"),                    # <- HU6: Login de empresa
    path("logout/", logout_view, name="logout"),                 # <- HU6: Logout
    path("register/", register_view, name="register"),           # <- HU7: Registro de empresa
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),  # <- HU8: Recuperar contraseña
    path("password-reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("devices/", device_list, name="device_list"),            # <- LISTA con filtro
    path("devices/<int:pk>/", device_detail, name="device_detail"),
    path("measurements/", measurement_list, name="measurement_list"),  # <- HU4: Lista de mediciones
    path("alerts/", alert_list, name="alert_list"),              # <- HU5: Lista de alertas de la semana
]
