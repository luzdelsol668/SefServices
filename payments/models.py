from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import PartnerCompany
from rides.models import Booking
from django.utils.translation import gettext_lazy as _
import secrets


class Payment(models.Model):
    payment_ref = models.CharField(max_length=255, null=True)
    trx_ref = models.CharField(max_length=255, null=True)
    price_id = models.TextField(null=True)
    product_id = models.TextField(null=True)
    payment_link = models.TextField(null=True)
    payment_id = models.TextField(null=True)
    payment_intent = models.TextField(null=True)
    reference_number = models.TextField(null=True)
    card_type_name = models.CharField(max_length=255, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    category = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    channel = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    paid_at = models.DateTimeField(null=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_ref

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_view_payment", _("Can view payment")),
            ("can_update_payment", _("Can update payment")),
            ("can_delete_payment", _("Can delete payment")),
        ]


@receiver(post_save, sender=Payment)
def generate_paymentRef(sender, instance, created, **kwargs):
    if created:
        while True:
            code = secrets.token_hex(8)
            if not Payment.objects.filter(payment_ref=code).exists():
                instance.payment_ref = str.upper(code)
                instance.save()
                break


class Payout(models.Model):
    partner = models.ForeignKey(PartnerCompany, on_delete=models.PROTECT)
    period_start = models.DateField()
    period_end = models.DateField()
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
