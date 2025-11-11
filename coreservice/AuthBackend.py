from django.contrib.auth.backends import ModelBackend

from accounts.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseRoleBackend(ModelBackend):

    role = None  # Must be overridden in subclasses

    def authenticate(self, request, email=None, password=None, **kwargs):

        if User.objects.filter(email=email).exists():

            user = User.objects.get(email=email)

            if user.role != self.role:
                return None

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
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:

            return None


class AdminBackend(BaseRoleBackend):
    role = User.Roles.ADMIN


class DriverBackend(BaseRoleBackend):
    role = User.Roles.DRIVER


class CustomerBackend(BaseRoleBackend):
    role = User.Roles.CUSTOMER

