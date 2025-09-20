from decimal import Decimal

from django.db import models
from django.utils import timezone

from accounts.models import PartnerCompany, Driver
from django.utils.translation import gettext_lazy as _
from sefservices import settings as env_variable
import uuid


def car_class_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"carclasses/{uuid.uuid4()}.{ext}"


# Create your models here.
class CarClass(models.Model):
    name = models.CharField(max_length=64, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_hour_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_hours = models.PositiveSmallIntegerField(default=1)
    airport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to=car_class_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_carclass", _("Can add carclass")),
            ("can_view_carclass", _("Can view carclass")),
            ("can_update_carclass", _("Can update carclass")),
            ("can_delete_carclass", _("Can delete carclass")),
        ]


class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    car_class = models.ForeignKey(CarClass, on_delete=models.PROTECT, related_name="vehicles")
    partner = models.ForeignKey(PartnerCompany, on_delete=models.CASCADE, related_name="vehicles")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles")
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    color = models.CharField(max_length=32, blank=True, default="")
    year = models.PositiveIntegerField()
    plate_number = models.CharField(max_length=32)
    capacity = models.PositiveSmallIntegerField(default=3)
    person_capacity = models.PositiveSmallIntegerField(default=2)
    luggage_capacity = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.make} {self.model} ({self.plate_number})"

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_vehicle", _("Can add vehicle")),
            ("can_view_vehicle", _("Can view vehicle")),
            ("can_update_vehicle", _("Can update vehicle")),
            ("can_delete_vehicle", _("Can delete vehicle")),
        ]


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    percent_off = models.PositiveSmallIntegerField(null=True, blank=True)
    amount_off = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_promo_code", _("Can add promocode")),
            ("can_view_promo_code", _("Can view promocode")),
            ("can_update_promo_code", _("Can update promocode")),
            ("can_delete_promo_code", _("Can delete promocode")),
        ]


class FareRule(models.Model):
    name = models.CharField(max_length=64, default=_("Default Fare Rule"))
    active = models.BooleanField(default=True)
    # Night multiplier
    night_enabled = models.BooleanField(default=True)
    night_start_hour = models.PositiveSmallIntegerField(default=22)  # 0..23
    night_end_hour = models.PositiveSmallIntegerField(default=6)     # 0..23 (can cross midnight)
    night_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.20"))
    # Weekend multiplier
    weekend_enabled = models.BooleanField(default=True)
    weekend_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.10"))
    # Weekend days: Python weekday() => Mon=0..Sun=6. Default: Sat(5), Sun(6)
    weekend_days = models.CharField(max_length=16, default="5,6")  # CSV of integers
    # Waiting time at pickup
    waiting_free_minutes = models.PositiveSmallIntegerField(default=5)
    waiting_charge_per_minute = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.75"))
    # Should waiting fees count towards driver commission?
    commission_applies_to_waiting = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-active", "-created_at"]
        default_permissions = ()
        permissions = [
            ("can_add_fare_rule", _("Can add fare rule")),
            ("can_view_fare_rule", _("Can view fare rule")),
            ("can_update_fare_rule", _("Can update fare rule")),
            ("can_delete_fare_rule", _("Can delete fare rule")),
        ]

    def __str__(self):
        return f"{self.name} ({'active' if self.active else 'inactive'})"

    @classmethod
    def get_active(cls):
        now = timezone.now()
        qs = cls.objects.filter(active=True)
        qs = qs.filter(models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now))
        qs = qs.filter(models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=now))
        return qs.first() or cls.objects.create(name="Auto-Default")


class Booking(models.Model):
    reference = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(env_variable.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    booking_type = models.CharField(max_length=100)
    car_class = models.ForeignKey(CarClass, on_delete=models.PROTECT, related_name="bookings")
    # when
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    duration_hours = models.PositiveSmallIntegerField(default=0)  # hourly bookings
    # where
    pickup_address = models.CharField(max_length=255)
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    dropoff_address = models.CharField(max_length=255, blank=True, default="")  # may be blank for hourly
    dropoff_lat = models.FloatField(null=True, blank=True)
    dropoff_lng = models.FloatField(null=True, blank=True)
    # estimations
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # for transfers
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="EUR")
    notes = models.TextField(blank=True, default="")
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        default_permissions = ()
        permissions = [
            ("can_add_booking", _("Can add booking")),
            ("can_view_booking", _("Can view booking")),
            ("can_update_booking", _("Can update booking")),
            ("can_delete_booking", _("Can delete booking")),
        ]

    def __str__(self):
        return f"{self.reference} - {self.booking_type} - {self.status}"


class BookingStop(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="stops")
    order = models.PositiveSmallIntegerField()
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    label = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Assignment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="assignment")
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        default_permissions = ()
        permissions = [
            ("can_add_assignment", _("Can add assignment")),
            ("can_view_assignment", _("Can view assignment")),
            ("can_update_assignment", _("Can update assignment")),
            ("can_delete_assignment", _("Can delete assignment")),
        ]


class TripEvent(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="events")
    at = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(max_length=40)  # ARRIVED, STARTED, COMPLETED, CANCELLED, ...
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)