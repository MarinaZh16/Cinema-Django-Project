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
]