from django.db import models
from django.contrib.auth.models import User


class User_settings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_machine = models.BooleanField(default=False)
    status = models.IntegerField(default=0)
    peer_id = models.TextField()
    machine_password = models.IntegerField(default=0)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'is_machine': self.is_machine,
            'machine_password': self.machine_password,
        }
