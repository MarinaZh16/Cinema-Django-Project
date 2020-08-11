from django.contrib.auth import login, authenticate, logout as logout_
from django.shortcuts import redirect, render
from user.forms import UserForm
from user.models import User
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from movies.api.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet


class RegisterView(FormView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('profile')
    template_name = 'registration/user_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_password(form.cleaned_data['password'])
        self.object.save()
        login(self.request, self.object)
        return super(RegisterView, self).form_valid(form)


def logout(request):
    logout_(request)
    return redirect('/')


class ProfilePage(TemplateView):
    template_name = 'registration/profile.html'

    def profile(self, request):
        return render(request, self.template_name)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
