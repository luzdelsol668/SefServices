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


ROLE_PROFILE = [
    ('ADMIN', 'Admin'),
    ('DRIVER', 'Driver'),
    ('CUSTOMER', 'Customer')
]


class User(AbstractUser):

    class Roles(models.TextChoices):
            ADMIN = "ADMIN", "Admin"
            DRIVER = "DRIVER", "Driver"
            CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER
    )
    username = None
    email = models.EmailField(unique=True)
    country = CountryField(max_length=255, blank_label=_("Choose a country"))
    city = models.CharField(max_length=255, null=True, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    is_blocked = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username} ({self.role})"


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    is_sms_enabled = models.BooleanField(default=True)
    is_email_enabled = models.BooleanField(default=True)
    is_marketing_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'

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




