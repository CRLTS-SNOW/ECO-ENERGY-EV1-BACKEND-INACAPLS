from datetime import timedelta
from django.db import models
from django.shortcuts import render
from django.utils import timezone
from .models import Organization, Device, Measurement, Alert
from django.shortcuts import get_object_or_404

def dashboard(request):
    # Organización activa
    org = Organization.objects.filter(deleted_at__isnull=True).first()
    week_ago = timezone.now() - timedelta(days=7)

    if not org:
        ctx = {
            "org": None,
            "latest_measurements": Measurement.objects.none(),
            "by_category": [],
            "by_zone": [],
            "alerts_week": [],
        }
        return render(request, "devices/dashboard.html", ctx)

    # Últimas 10 mediciones
    latest_measurements = (
        Measurement.objects
        .filter(organization=org, deleted_at__isnull=True)
        .select_related("device")
        .order_by("-measured_at")[:10]
    )

    # Conteo por categoría (mostramos nombre real)
    by_category = (
        Device.objects
        .filter(organization=org, deleted_at__isnull=True)
        .values("category__name")   # ✅ CORREGIDO
        .annotate(total=models.Count("id"))
        .order_by("category__name")
    )

    # Conteo por zona (mostramos nombre real)
    by_zone = (
        Device.objects
        .filter(organization=org, deleted_at__isnull=True)
        .values("zone__name")   # ✅ CORREGIDO
        .annotate(total=models.Count("id"))
        .order_by("zone__name")
    )

    # Alertas de la última semana
    alerts_week = (
        Alert.objects
        .filter(organization=org, occurred_at__gte=week_ago, deleted_at__isnull=True)
        .values("severity")
        .annotate(total=models.Count("id"))
        .order_by("severity")
    )

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

def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk, deleted_at__isnull=True)
    measurements = (
        Measurement.objects
        .filter(device=device, deleted_at__isnull=True)
        .order_by("-measured_at")[:50]
    )
    alerts = (
        Alert.objects
        .filter(device=device, deleted_at__isnull=True)
        .order_by("-occurred_at")[:20]
    )
    return render(request, "devices/device_detail.html", {
        "device": device,
        "measurements": measurements,
        "alerts": alerts,
    })
