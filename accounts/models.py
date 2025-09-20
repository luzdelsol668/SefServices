import stripe
from django.db import models

# Create your models here.
from django.conf import settings
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
import uuid


class Customer(AbstractUser):
    username = None  # Remove username field
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    country = CountryField(max_length=255, blank_label=_("Choose a country"))
    city = models.CharField(max_length=255, null=True, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_sms_enabled = models.BooleanField(default=True)
    is_email_enabled = models.BooleanField(default=True)
    is_marketing_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group,
        related_name="customer_set",
        related_query_name="customer",
        blank=True,
        verbose_name="groups",
        help_text="Groups this customer belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customer_set",
        related_query_name="customer",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this customer."
    )

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_customer", _("Can add customer")),
            ("can_view_customer", _("Can view customer")),
            ("can_update_customer", _("Can update customer")),
            ("can_delete_customer", _("Can delete customer")),
        ]


class PaymentMethod(models.Model):

    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payment_methods")
    payment_method_id = models.CharField(max_length=255)
    setup_intent_id = models.CharField(max_length=255)
    brand = models.CharField(max_length=50)
    last4 = models.CharField(max_length=4)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} ****{self.last4}"


class PartnerCompany(models.Model):
    reference = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=2)
    payout_currency = models.CharField(max_length=3, default="EUR")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_company", _("Can add company")),
            ("can_view_company", _("Can view company")),
            ("can_update_company", _("Can update company")),
            ("can_delete_company", _("Can delete company")),
        ]


class Driver(AbstractUser):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"

    username = None  # Remove username field
    reference = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    country = CountryField(max_length=255, blank_label=_("Choose a country"))
    city = models.CharField(max_length=255, null=True, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    is_blocked = models.BooleanField(default=False)
    partner = models.ForeignKey(PartnerCompany, on_delete=models.CASCADE, related_name="drivers")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)  # 1..5
    kyc_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name="driver_set",
        related_query_name="driver",
        blank=True,
        verbose_name="groups",
        help_text="Groups this driver belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="driver_set",
        related_query_name="driver",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this driver."
    )

    def __str__(self):
        return f'{_("Driver - ")}{self.reference}'

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_driver", _("Can add driver")),
            ("can_view_driver", _("Can view driver")),
            ("can_update_driver", _("Can update driver")),
            ("can_delete_driver", _("Can delete driver")),
        ]


class DriverDocument(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="documents")
    type = models.CharField(max_length=50)  # license, insurance, vehicle_permit
    file = models.FileField(upload_to="driver_docs/")
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_driver_doc", _("Can add driver document")),
            ("can_view_driver_doc", _("Can view driver document")),
            ("can_update_driver_doc", _("Can update driver document")),
            ("can_delete_driver_doc", _("Can delete driver document")),
        ]
