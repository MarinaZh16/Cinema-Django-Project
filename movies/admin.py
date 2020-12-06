from django.contrib import admin
from . import models


class FilmAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'film_duration']


class SeanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'film', 'beginning', 'end', 'seats']


class HallAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class TicketAdmin(admin.ModelAdmin):
    list_display = ['seance', 'row', 'seat']


admin.site.register(models.Film, FilmAdmin)
admin.site.register(models.Seance, SeanceAdmin)
admin.site.register(models.Hall, HallAdmin)
admin.site.register(models.Ticket, TicketAdmin)