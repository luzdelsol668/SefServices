from django.contrib.auth.backends import ModelBackend
from accounts.models import Customer


class UserAuthBackend(ModelBackend):

    def authenticate(self, request, email=None, password=None, **kwargs):

        if Customer.objects.filter(email=email).exists():

            user = Customer.objects.get(email=email)

            if user.password:
                if user.check_password(password):

                    return user
                else:
                    return None
            else:

                return None
        else:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:

            return None