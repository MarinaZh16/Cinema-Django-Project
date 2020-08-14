from django.contrib.auth import login, authenticate, logout as logout_
from django.shortcuts import redirect, render
from user.forms import UserForm
from user.models import User
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from movies.api.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser


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
    permission_classes = [IsAdminUser]


class ObtainTokenView(APIView):
    http_method_names = ['post']
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user = authenticate(request,
                            username=self.request.data.get('username'),
                            password=self.request.data.get('password'))
        if user is not None:
            return Response(str(Token.objects.get(user=user)), 200)
        else:
            return HttpResponse(status=401)