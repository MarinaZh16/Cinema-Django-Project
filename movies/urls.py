from django.urls import path
from movies import views

urlpatterns = [
    path('', views.SeancesTodayListView.as_view(), name='seances_today'),
    path('tomorrow/<int:delta>/', views.SeancesTodayListView.as_view(), name='seances_tomorrow'),
    path('create/', views.FilmCreate.as_view(), name='add_film'),
    path('films/<int:pk>/', views.FilmDetailView.as_view(), name='film_by_id'),
    path('films/', views.FilmListView.as_view(), name='all_films'),
    path('hall/', views.HallListView.as_view(), name='all_halls'),
    path('hall/create/', views.HallCreate.as_view(), name='add_hall'),
    path('hall/<int:pk>/', views.HallDetailView.as_view(), name='hall_by_id'),
    path('seance/', views.SeanceListView.as_view(), name='all_seances'),
    path('seance/sorted/<int:ord>/', views.SeanceListView.as_view(), name='seances_sorted'),
    path('seance/create/', views.SeanceCreate.as_view(), name='add_seance'),
    path('edit/<int:pk>/', views.SeanceUpdate.as_view(), name='edit_seance'),
    path('seance/<int:pk>/', views.SeanceDetailView.as_view(), name='seance_by_id'),
    path('ticket/', views.TicketListView.as_view(), name='all_tickets'),
    path('ticket/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_by_id'),
    path('json_tickets/<int:pk>/', views.TicketsAPIView.as_view(), name='user_tickets_detail'),
    path('api_films/', views.film_list, name='films_list'),
    path('api_films/<int:pk>/', views.film_list, name='films_detail'),
    path('api_seances/', views.seance_list, name='seances_list'),
    path('api_seances/<int:pk>/', views.seance_list, name='seances_detail'),
    path('api_halls/', views.hall_list, name='halls_list'),
    path('api_halls/<int:pk>/', views.hall_list, name='halls_detail'),
]