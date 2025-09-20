import os
import requests as makeRequest
import stripe
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from stripe.api_resources import setup_intent

from accounts.models import PaymentMethod as UserPaymentMethod, PaymentMethod
from sefservices import settings as env_variable


def get_client_location(user_ip=None):
    url = f"https://api.seeip.org/geoip/{user_ip}"
    response = makeRequest.get(url, verify=False).json()
    data = {
        'country': response['country'],

        'ip': response['ip'],
    }
    if "city" in data:
        data['city'] = response['city']
    else:
        data['city'] = ""

    return data


def is_disposable(email):
    email = email[str(email).find('@') + 1:]
    emails = []
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'disposable.txt')
    disposable_mails = open(file_path, 'r+')
    for disposable_mail in disposable_mails:
        emails.append(disposable_mail.rstrip())

    if str(email) in emails:
        return True
    else:
        return False


class StripeManager:

    def __init__(self):
        self.api_key = env_variable.STRIPE_API_KEY
        stripe.api_key = self.api_key

    def create_stripe_customer(self, user):

        search = stripe.Customer.search(
            query="email:"'\'' + user.email + "\'",
        )

        if len(search.data) == 0:

            customer = stripe.Customer.create(
                name=f"{user.first_name} {user.last_name}",
                email=user.email,
                address={"country": user.country},
            )
            user.stripe_customer_id = customer["id"]
            user.save()
            return user.stripe_customer_id
        else:
            customer_id = search.data[0]["id"]
            user.stripe_customer_id = customer_id
            user.save()

            return user.stripe_customer_id

    def create_card_intent(self, user):

        setup_intent = stripe.SetupIntent.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"]
        )

        return setup_intent

    def add_payment_method(self, user, payment_method_id, make_default=False):

        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=user.stripe_customer_id,
        )

        pm = stripe.Customer.retrieve_payment_method(f"{user.stripe_customer_id}", f"{payment_method_id}")
        card = pm['card']

        with transaction.atomic():
            new_pm = UserPaymentMethod.objects.create(
                user=user,
                payment_method_id=payment_method_id,
                brand=card['brand'],
                last4=card['last4'],
                exp_month=card['exp_month'],
                exp_year=card['exp_year'],
                is_default=make_default,
            )

            if make_default:
                stripe.Customer.modify(
                    user.stripe_customer_id,
                    invoice_settings={"default_payment_method": payment_method_id}
                )
                new_pm.is_default = True
                new_pm.save()

    def remove_payment_method(self, user, payment_method_id):

        payment_method = get_object_or_404(PaymentMethod, payment_method_id=payment_method_id, user=user)
        payment_method.delete()

        try:
            stripe.PaymentMethod.detach(payment_method_id)
        except stripe.error.InvalidRequestError:
            pass  # Already detached or invalid

    def set_default_payment_method(self, user, payment_method_id):

        user.payment_methods.update(is_default=False)

        payment_method = get_object_or_404(PaymentMethod, payment_method_id=payment_method_id, user=user)
        payment_method.is_default = True
        payment_method.save()

        stripe.Customer.modify(
            user.stripe_customer_id,
            invoice_settings={"default_payment_method": payment_method_id}
        )


    def create_order(self):
        product = stripe.Product.create(
            name=f"Paiement de la Facture NÂ° {self.payment.invoice.invoice_number}",
            description="Paiement des frais de rÃ©servation",
            images=["https://cetef.tg/wp-content/uploads/2024/09/footer_logo.png"],
        )

        price = stripe.Price.create(
            unit_amount=(round(self.payment.amount)),
            currency=f"xof".lower(),
            product=f"{product.id}",
        )

        '''payment_link = stripe.PaymentLink.create(
            payment_method_types=['card'],
            line_items=[
                {
                    "price": f"{price.id}",
                    "quantity": 1,
                },
            ],
            #currency="eur",
            after_completion={
                "type": "hosted_confirmation",
                "hosted_confirmation": {
                    "custom_message": "Merci. Nous allons traiter votre opÃƒÂ©ration."
                },
            },
            custom_fields=[{
                "key": "motif",
                "label": {
                    "type": "custom",
                    "custom": "Motif d'envoi"
                },
                "type": "dropdown",
                "dropdown": {
                    "options": [
                        {"label": "Don ou Aide humanitaire", "value": "donation"},
                        {"label": "Ãƒâ€°pargne et investissement personnel", "value": "personal"},
                        {"label": "Ãƒâ€°tudes", "value": "etd"},
                        {"label": "Ãƒâ€°vÃƒÂ©nements familiaux", "value": "eventfami"},
                        {"label": "Investissements", "value": "invest"},
                        {"label": "Soutien ÃƒÂ©conomique", "value": "stcono"},
                        {"label": "Soutien familial", "value": "stfami"},
                        {"label": "Soutien mÃƒÂ©dical", "value": "stmedico"},
                        {"label": "Remboursement de prÃƒÂªts", "value": "loan"},
                    ]
                }
            }]
        )'''

        success_url = f"{env_variable.SITE_URL}{reverse('exhibitor:exhibitor_payment_done')}"
        payment_session = stripe.checkout.Session.create(
            success_url=success_url,
            client_reference_id=f"{self.payment.payment_ref}",
            line_items=[{"price": f"{price.id}", "quantity": 1}],
            mode="payment",
        )

        self.payment.payment_link = payment_session.url
        self.payment.price_id = price.id
        self.payment.product_id = product.id
        self.payment.payment_id = payment_session.id
        self.payment.save()

        return f"{payment_session.url}"
