# from django.contrib import messages
from datetime import datetime
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse


class LogoutNotActive:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            if datetime.timestamp(datetime.now()) - datetime.timestamp(request.user.last_login) < 10:
                request.user.save()
            if (datetime.timestamp(datetime.now()) - datetime.timestamp(request.user.last_echo)) > 300:
                logout(request)
                return HttpResponseRedirect(reverse('homepage'))
            request.user.save()
        response = self.get_response(request)
        return response

