from django.shortcuts import render, redirect
from movies import models, forms
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta, date, datetime
from django.contrib import messages
from movies.api.serializers import FilmSerializer, SeanceSerializer, TicketSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from movies.api.permissions import AuthorOnlyPermission


# class ProtectedTemplateView(UserPassesTestMixin, TemplateView):
#     def test_func(self):
#         return self.request.user.is_superuser
#
#     def dispatch(self, request, *args, **kwargs):
#         user_test_result = self.get_test_func()()
#         if not user_test_result:
#             return redirect('/')
#         return super().dispatch(request, *args, **kwargs)


def index(request):
    return render(request, 'movies/homepage.html')


class FilmCreate(CreateView):
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
    model = models.Film
    ordering = '-title'
    template_name = 'movies/seances_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        film = []
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
        film_list = set(film)
        context.update(dict(film_list=film_list, seances=seances, view_date=view_date,
                            today=today, delta=delta, choice=choice))
        return context


class HallCreate(CreateView):
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
        seats = [i for i in range(1, hall.seat + 1)]
        rows = [i for i in range(1, hall.row + 1)]
        context = super().get_context_data()
        context.update(dict(seats=seats, rows=rows))
        return context


class SeanceCreate(CreateView):
    model = models.Seance
    form_class = forms.SeanceForm
    success_url = reverse_lazy('all_seances')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super().form_valid(form)


class SeanceUpdate(UpdateView):
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
            messages.error(request, 'Time is up! You can not byu ticket on this seance!')
        else:
            for key, value in request.POST.items():
                if key.startswith('seat'):
                    row, seat = key.split('-')[-2:]
                    ticket_check = models.Ticket.objects.filter(seance=seance, row=row, seat=seat)
                    if seance.seats == 0:
                        messages.error(request, 'Sorry, all seats already taken! Pick another seance!')
                    elif ticket_check:
                        messages.error(request, 'seat %s in row %s is already taken! Pick another one!' % (seat, row))
                    else:
                        ticket = models.Ticket(user=user, seance=seance, row=row, seat=seat)
                        ticket.save()
                        user.total_sum += ticket.seance.price
                        user.save()
                        seance.seats -= 1
                        seance.save()
        # return HttpResponseRedirect(reverse_lazy('all_tickets'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class SeanceListView(ListView):
    model = models.Seance

    def get_context_data(self, *, object_list=None, **kwargs):
        # context = super(SeanceListView, self).get_context_data(**kwargs)
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
        tickets = models.Ticket.objects.all()
        user = self.request.user
        seances = []
        for ticket in tickets:
            if ticket.user == user:
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
    permission_classes = [IsAuthenticated, AuthorOnlyPermission]


class SeanceViewSet(ModelViewSet):
    queryset = models.Seance.objects.all()
    serializer_class = SeanceSerializer
    permission_classes = [IsAdminUser, ]


class TicketViewSet(ModelViewSet):
    queryset = models.Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AuthorOnlyPermission]

    def perform_create(self, serializer):
        user = self.request.user
        user.save()
        return serializer.save(user=user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TicketsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            ticket = models.Ticket.objects.get(id=kwargs.get('pk'))
            data = TicketSerializer(ticket).data
        else:
            tickets = models.Ticket.objects.filter(user=request.user)
            data = TicketSerializer(tickets, many=True).data
        return Response(data, status=200)
