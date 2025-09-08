# ecoEnergy/devices/urls.py
from django.urls import path
from .views import dashboard, device_list, device_detail, measurement_list

app_name = "devices"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("devices/", device_list, name="device_list"),            # <- LISTA con filtro
    path("devices/<int:pk>/", device_detail, name="device_detail"),
    path("measurements/", measurement_list, name="measurement_list"),  # <- HU4: Lista de mediciones
]
