from django.contrib.auth.models import AbstractUser
from django.db import models

from sefservices import settings


# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_admin", "Peut ajouter un administrateur"),
            ("can_view_admin", "Peut voir un administrateur"),
            ("can_view_dashboard", "Peut voir le board"),
            ("can_update_admin", "Peut mettre à jour un administrateur"),
            ("can_delete_admin", "Peut supprimer un administrateur"),
        ]
