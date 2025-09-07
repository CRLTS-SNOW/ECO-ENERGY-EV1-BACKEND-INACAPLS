from django.urls import path
from . import views

app_name = "devices"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("devices/<int:pk>/", views.device_detail, name="device_detail"),
]
