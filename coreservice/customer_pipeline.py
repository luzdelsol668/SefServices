from coreservice.helpers import StripeManager
from accounts.models import Customer
from django.shortcuts import redirect
from social_core.pipeline.partial import partial


def save_profile(backend, user, response, *args, **kwargs):

    user = Customer.objects.get(pk=user.id)
    if user.customerId is None or user.customerId == "":
        stripe_manager = StripeManager()
        stripe_manager.createCustomer(email=user.email)


@partial
def collect_password(strategy, backend, request, details, user=None, is_new=False, *args, **kwargs):
    # session 'local_password' is set by the pipeline infrastructure
    # because it exists in FIELDS_STORED_IN_SESSION
    local_password = strategy.session_get('local_password', None)
    request.session['backend'] = backend.name

    if is_new:

        if not local_password:

            return redirect("collect_password")

        if user:

            #user = User.objects.create(email=details['email'])
            user.set_password(local_password)
            user.save()

    # continue the pipeline
    return