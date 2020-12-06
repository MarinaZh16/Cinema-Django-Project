from datetime import timedelta, date, datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django_filters.rest_framework import DjangoFilterBackend
from movies.api.permissions import AuthorOnlyPermission
from movies.api.serializers import FilmSerializer, SeanceSerializer, TicketSerializer, HallSerializer
from movies import models, forms


class ProtectedTemplateView(UserPassesTestMixin):
    """checking if user is superuser, and if not, redirect to the home page.
    prevents regular users from using functions that they are not supposed to use"""
    def test_func(self):
        return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)


def index(request):
    return render(request, 'movies/homepage.html')


class FilmCreate(ProtectedTemplateView, CreateView):
    model = models.Film
    form_class = forms.FilmForm
    success_url = reverse_lazy('all_films')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super().form_valid(form)


class FilmDetailView(DetailView):
    model = models.Film
    template_name = 'movies/film_by_id.html'


class FilmListView(ListView):
    model = models.Film
    queryset = models.Film.objects.all()
    ordering = '-title'
    template_name = 'movies/film_list.html'


class SeancesTodayListView(ListView):
    """list of seances for today and tomorrow"""
    model = models.Film
    ordering = '-title'
    template_name = 'movies/seances_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        film = []
        """we get data from the user from the template (show the list of sessions for today or tomorrow)"""
        delta = self.kwargs.get('delta' or None)
        choice = 'today'
        if delta:
            choice = 'tomorrow'
            seances = models.Seance.objects.filter(
                beginning__range=(date.today() + timedelta(days=1),
                                  date.today() + timedelta(days=2)))
            view_date = date.today() + timedelta(days=1)
            for seance in seances:
                film.append(seance.film)
        else:
            seances = models.Seance.objects.filter(
                beginning__range=(date.today(),
                                  date.today() + timedelta(days=1)))
            for seance in seances:
                film.append(seance.film)
            view_date = date.today()
        today = datetime.now()
        context = super().get_context_data()
        """we make a set so that the films do not repeat"""
        film_list = set(film)
        context.update(dict(film_list=film_list, seances=seances, view_date=view_date,
                            today=today, delta=delta, choice=choice))
        return context


class HallCreate(ProtectedTemplateView, CreateView):
    model = models.Hall
    form_class = forms.HallForm
    success_url = reverse_lazy('all_halls')


class HallListView(ListView):
    model = models.Hall
    queryset = models.Hall.objects.all()
    ordering = '-name'


class HallDetailView(DetailView):
    model = models.Hall
    template_name = 'movies/hall_by_id.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        hall = self.model.objects.get(id=self.kwargs['pk'])
        """generate lists of seats and rows for drawing in the template"""
        seats = [i for i in range(1, hall.seat + 1)]
        rows = [i for i in range(1, hall.row + 1)]
        context = super().get_context_data()
        context.update(dict(seats=seats, rows=rows))
        return context


class SeanceCreate(ProtectedTemplateView, CreateView):
    model = models.Seance
    form_class = forms.SeanceForm
    success_url = reverse_lazy('all_seances')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.seats = self.object.hall.total_seats
        self.object.save()
        return super().form_valid(form)


class SeanceUpdate(ProtectedTemplateView, UpdateView):
    model = models.Seance
    form_class = forms.SeanceForm
    success_url = reverse_lazy('all_seances')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.seats = self.object.hall.total_seats
        self.object.save()
        return super().form_valid(form)


class SeanceDetailView(DetailView):
    model = models.Seance
    template_name = 'movies/seance_by_id.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """we get data about tickets purchased for this seance in order to draw the occupied seats"""
        seance = self.model.objects.get(id=self.kwargs['pk'])
        tickets = models.Ticket.objects.filter(seance=seance)
        context = super().get_context_data()
        context.update(dict(tickets=tickets))
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        seance_id = request.POST.get('seance_id')
        seance = models.Seance.objects.get(id=seance_id)
        if seance.beginning < timezone.now():
            """check if the seance has started"""
            messages.error(request, 'Time is up! You can not buy ticket on this seance!')
        else:
            for key, value in request.POST.items():
                if key.startswith('seat'):
                    row, seat = key.split('-')[-2:]
                    """check the seats marked by the user"""
                    ticket_check = models.Ticket.objects.filter(seance=seance, row=row, seat=seat)
                    if seance.seats == 0:
                        """check if there are free seats"""
                        messages.error(request, 'Sorry, all seats already taken! Pick another seance!')
                    elif ticket_check:
                        """check if the selected seats are free"""
                        messages.error(request, 'seat %s in row %s is already taken! Pick another one!' % (seat, row))
                    else:
                        ticket = models.Ticket(user=user, seance=seance, row=row, seat=seat)
                        ticket.save()
                        seance.seats -= 1
                        seance.save()
            return HttpResponseRedirect(reverse_lazy('all_tickets'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class SeanceListView(ListView):
    """list of all seances"""
    model = models.Seance

    def get_context_data(self, *, object_list=None, **kwargs):
        ordering = self.kwargs.get('ord' or None)
        choice = 'title'
        seance_list = models.Seance.objects.all().order_by('film__title')
        if ordering == 1:
            seance_list = models.Seance.objects.all().order_by('price')
            choice = 'price'
        elif ordering == 2:
            seance_list = models.Seance.objects.all().order_by('beginning')
            choice = 'beginning'
        context = super().get_context_data()
        context.update(dict(seance_list=seance_list, choice=choice))
        return context


class TicketListView(ListView):
    model = models.Ticket
    ordering = ['seance__film__title']

    def get_context_data(self, *, request=None,  object_list=None, **kwargs):
        """the list of tickets purchased by the user, displayed by seance (several tickets per seance)"""
        tickets = models.Ticket.objects.all()
        user = self.request.user
        seances = []
        for ticket in tickets:
            if ticket.user == user or user.is_superuser:
                seances.append(models.Seance.objects.get(id=ticket.seance.id))
        seance_list = set(seances)
        context = super().get_context_data()
        context.update(dict(seance_list=seance_list))
        return context


class TicketDetailView(DetailView):
    model = models.Ticket
    template_name = 'movies/ticket_by_id.html'


"""------------------------------------------------------------------------------------------------------------------"""


class FilmViewSet(ModelViewSet):
    queryset = models.Film.objects.all()
    serializer_class = FilmSerializer
    permission_classes = [IsAdminUser]


class HallVieSet(ModelViewSet):
    queryset = models.Hall.objects.all()
    serializer_class = HallSerializer
    permission_classes = [IsAdminUser]


class SeanceViewSet(ModelViewSet):
    queryset = models.Seance.objects.all()
    serializer_class = SeanceSerializer
    permission_classes = [IsAdminUser]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('hall', 'beginning')


class TicketViewSet(ModelViewSet):
    queryset = models.Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AuthorOnlyPermission]


"""------------------------------------------------------------------------------------------------------------------"""


class TicketsAPIView(APIView):
    serializer_class = TicketSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            ticket = models.Ticket.objects.get(id=kwargs.get('pk'))
            if request.user == ticket.user or request.user.is_superuser:
                data = TicketSerializer(ticket).data
        else:
            tickets = models.Ticket.objects.filter(user=request.user)
            data = TicketSerializer(tickets, many=True).data
        return Response(data, status=200)

    def perform_create(self, serializer):
        user = self.request.user
        return serializer.save(user=user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@api_view(['GET'])
def film_list(request, *args, **kwargs):
    if request.method == 'GET':
        if kwargs.get('pk'):
            film = models.Film.objects.get(id=kwargs.get('pk'))
            data = FilmSerializer(film).data
        else:
            films = models.Film.objects.all()
            data = FilmSerializer(films, many=True).data
        return Response(data, status=200)


@api_view(['GET'])
def seance_list(request, *args, **kwargs):
    if request.method == 'GET':
        if kwargs.get('pk'):
            seance = models.Seance.objects.get(id=kwargs.get('pk'))
            data = SeanceSerializer(seance).data
        else:
            seances = models.Seance.objects.all()
            data = SeanceSerializer(seances, many=True).data
        return Response(data, status=200)


@api_view(['GET'])
def hall_list(request, *args, **kwargs):
    if request.method == 'GET':
        if kwargs.get('pk'):
            hall = models.Hall.objects.get(id=kwargs.get('pk'))
            data = HallSerializer(hall).data
        else:
            halls = models.Hall.objects.all()
            data = HallSerializer(halls, many=True).data
        return Response(data, status=200)


