from django.shortcuts import get_object_or_404, render
from .models import Device

def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk, deleted_at__isnull=True)
    return render(request, "device_detail.html", {"device": device})
