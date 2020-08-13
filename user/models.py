from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import uuid as uuid







class User(AbstractUser):
    last_echo = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=32, blank=True, null=True)
    total_sum = models.FloatField(default=0, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4()).replace('-', '')
        return super(User, self).save(*args, **kwargs)