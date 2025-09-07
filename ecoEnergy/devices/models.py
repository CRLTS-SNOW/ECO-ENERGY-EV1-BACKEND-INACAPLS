from django.db import models
from django.utils import timezone


class TimeStampedSoftDeleteModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"])


class Organization(TimeStampedSoftDeleteModel):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = "organization"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(TimeStampedSoftDeleteModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=120)

    class Meta:
        db_table = "category"
        unique_together = [("organization", "name")]
        indexes = [models.Index(fields=["organization", "name"])]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Zone(TimeStampedSoftDeleteModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=120)

    class Meta:
        db_table = "zone"
        unique_together = [("organization", "name")]
        indexes = [models.Index(fields=["organization", "name"])]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Device(TimeStampedSoftDeleteModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="devices")
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="devices")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "device"
        unique_together = [("organization", "name")]
        indexes = [
            models.Index(fields=["organization", "category"]),
            models.Index(fields=["organization", "zone"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Measurement(TimeStampedSoftDeleteModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="measurements")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="measurements")
    measured_at = models.DateTimeField(default=timezone.now, db_index=True)
    value = models.DecimalField(max_digits=12, decimal_places=3)  # kWh u otra unidad acordada

    class Meta:
        db_table = "measurement"
        indexes = [
            models.Index(fields=["organization", "measured_at"]),
            models.Index(fields=["device", "-measured_at"]),
        ]
        ordering = ["-measured_at"]

    def __str__(self):
        return f"{self.device} @ {self.measured_at:%Y-%m-%d %H:%M:%S} = {self.value}"


class Alert(TimeStampedSoftDeleteModel):
    class Severity(models.TextChoices):
        CRITICAL = "critical", "Grave"
        HIGH = "high", "Alta"
        MEDIUM = "medium", "Media"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="alerts")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="alerts")
    severity = models.CharField(max_length=10, choices=Severity.choices, db_index=True)
    message = models.CharField(max_length=255)
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "alert"
        indexes = [
            models.Index(fields=["organization", "severity", "occurred_at"]),
            models.Index(fields=["device", "-occurred_at"]),
        ]
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_severity_display()} - {self.device}: {self.message}"
