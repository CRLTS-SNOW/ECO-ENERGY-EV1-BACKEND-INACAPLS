from datetime import timedelta

from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Alert, Category, Device, Measurement, Organization


# =========================
# Dashboard (HU1)
# =========================
def dashboard(request):
    """
    Carga el panel con:
      - Últimas mediciones
      - Conteo de dispositivos por categoría y por zona
      - Alertas últimos 7 días

    Incluye una resolución robusta de 'org' por si no existe una Organization
    con deleted_at NULL, pero sí hay datos cargados en otras tablas.
    """
    # 1) Intento normal
    org = Organization.objects.filter(deleted_at__isnull=True).first()

    # 2) Fallback si no hay org 'activa' pero hay datos cargados
    if not org:
        oid = (
            Device.objects.values_list("organization_id", flat=True).first()
            or Category.objects.values_list("organization_id", flat=True).first()
            or Measurement.objects.values_list("organization_id", flat=True).first()
            or Alert.objects.values_list("organization_id", flat=True).first()
        )
        if oid:
            org = Organization.objects.filter(id=oid).first()

    week_ago = timezone.now() - timedelta(days=7)

    if not org:
        # Sin organización ni datos: devolver bloques vacíos
        ctx = {
            "org": None,
            "latest_measurements": Measurement.objects.none(),
            "by_category": [],
            "by_zone": [],
            "alerts_week": [],
        }
        return render(request, "devices/dashboard.html", ctx)

    # -------- Datos del dashboard --------
    latest_measurements = (
        Measurement.objects.filter(organization=org, deleted_at__isnull=True)
        .select_related("device")
        .order_by("-measured_at")[:10]
    )

    by_category = (
        Device.objects.filter(organization=org, deleted_at__isnull=True)
        .values("category__name")
        .annotate(total=models.Count("id"))
        .order_by("category__name")
    )

    by_zone = (
        Device.objects.filter(organization=org, deleted_at__isnull=True)
        .values("zone__name")
        .annotate(total=models.Count("id"))
        .order_by("zone__name")
    )

    alerts_week = (
        Alert.objects.filter(
            organization=org, occurred_at__gte=week_ago, deleted_at__isnull=True
        )
        .values("severity")
        .annotate(total=models.Count("id"))
        .order_by("severity")
    )
    
    # Convertir severity a display names
    severity_display = {
        'critical': 'Grave',
        'high': 'Alta', 
        'medium': 'Media'
    }
    
    alerts_week = [
        {
            'severity': item['severity'],
            'severity_display': severity_display.get(item['severity'], item['severity']),
            'total': item['total']
        }
        for item in alerts_week
    ]

    return render(
        request,
        "devices/dashboard.html",
        {
            "org": org,
            "latest_measurements": latest_measurements,
            "by_category": by_category,
            "by_zone": by_zone,
            "alerts_week": alerts_week,
        },
    )


# =========================
# Listado de dispositivos (HU2)
# =========================
def device_list(request):
    """
    Lista dispositivos con filtro por categoría y paginación.
    """
    org = Organization.objects.filter(deleted_at__isnull=True).first()
    if not org:
        ctx = {"devices": [], "categories": [], "selected_category": ""}
        return render(request, "devices/device_list.html", ctx)

    selected = request.GET.get("category", "").strip()

    qs = (
        Device.objects.filter(organization=org, deleted_at__isnull=True)
        .select_related("category", "zone")
        .order_by("name")
    )

    if selected:
        qs = qs.filter(category__id=selected)

    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    devices = paginator.get_page(page)

    categories = (
        Category.objects.filter(organization=org, deleted_at__isnull=True)
        .order_by("name")
    )

    return render(
        request,
        "devices/device_list.html",
        {
            "devices": devices,
            "categories": categories,
            "selected_category": selected,
        },
    )


# =========================
# Detalle de dispositivo (HU3)
# =========================
def device_detail(request, pk):
    """
    Muestra la ficha completa de un dispositivo con:
    - Información básica (nombre, categoría, zona)
    - Tabla de mediciones ordenadas por fecha desc
    - Lista de alertas con severidad
    - Mensajes de estado vacío cuando no hay datos
    """
    device = get_object_or_404(Device, pk=pk, deleted_at__isnull=True)
    
    # Obtener mediciones del dispositivo ordenadas por fecha descendente
    measurements = (
        Measurement.objects.filter(device=device, deleted_at__isnull=True)
        .order_by("-measured_at")
    )
    
    # Obtener alertas del dispositivo ordenadas por fecha descendente
    alerts = (
        Alert.objects.filter(device=device, deleted_at__isnull=True)
        .order_by("-occurred_at")
    )
    
    return render(
        request,
        "devices/device_detail.html", 
        {
            "device": device,
            "measurements": measurements,
            "alerts": alerts,
        }
    )


# =========================
# Listado de mediciones (HU4)
# =========================
def measurement_list(request):
    """
    Lista todas las mediciones con paginación (máximo 50 por página).
    """
    org = Organization.objects.filter(deleted_at__isnull=True).first()
    if not org:
        ctx = {"measurements": [], "org": None}
        return render(request, "devices/measurement_list.html", ctx)

    qs = (
        Measurement.objects.filter(organization=org, deleted_at__isnull=True)
        .select_related("device")
        .order_by("-measured_at")
    )

    paginator = Paginator(qs, 50)  # Máximo 50 registros por página
    page = request.GET.get("page")
    measurements = paginator.get_page(page)

    return render(
        request,
        "devices/measurement_list.html",
        {
            "measurements": measurements,
            "org": org,
        },
    )
