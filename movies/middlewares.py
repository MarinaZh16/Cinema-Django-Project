# from django.contrib import messages
from datetime import date, timedelta
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from movies import models


class SeanceNotEditable:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if request.user.is_superuser:
            seances = models.Seance.objects.filter(is_editable=True)
            for seance in seances:
                if seance.seats < seance.hall.total_seats or seance.beginning < timezone.now():
                    seance.is_editable = False
                    seance.save()
        response = self.get_response(request)
        return response
