from django.db import models
from django.contrib.auth.models import AbstractUser
from movies.models import Ticket


class User(AbstractUser):
    """activity recording field"""
    last_echo = models.DateTimeField(auto_now=True)

    @property
    def total_sum(self):
        """calculation of the amount spent on tickets"""
        total_sum = 0
        tickets = Ticket.objects.filter(user=self)
        for ticket in tickets:
            total_sum += ticket.seance.price
        return total_sum

    def save(self, *args, **kwargs):
        # if not self.token:
        #     self.token = str(uuid.uuid4()).replace('-', '')
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"

