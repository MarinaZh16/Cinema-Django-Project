from django.forms import ModelForm
from movies import models
from django import forms
from tempus_dominus.widgets import DatePicker, DateTimePicker
import datetime
from django.utils import timezone

from django.contrib import messages


class FilmForm(ModelForm):
    start_show = forms.DateTimeField(widget=DatePicker)
    # end_show = forms.DateTimeField(widget=DatePicker)
    film_duration = forms.CharField(help_text='minutes')

    class Meta:
        model = models.Film
        fields = '__all__'


class HallForm(ModelForm):
    class Meta:
        model = models.Hall
        fields = '__all__'


class SeanceForm(ModelForm):
    beginning = forms.DateTimeField(widget=DateTimePicker)

    def clean_beginning(self):
        beginning = self.cleaned_data['beginning']
        film = models.Film.objects.get(title=self.cleaned_data['film'])
        if datetime.date.today() > film.end_show:
            raise forms.ValidationError('This movie has expired!')
        elif film.start_show > beginning.date() or beginning.date() > film.end_show:
            raise forms.ValidationError('That date is out of range. Pick date between %s - %s' %
                                        (film.start_show, film.end_show))
        elif beginning < timezone.now():
            raise forms.ValidationError('This time has passed')
        else:
            seance_list = models.Seance.objects.filter(hall=self.cleaned_data['hall'],
                                                       beginning__date=beginning.date())
            if seance_list:
                end = beginning + film.duration
                for seance in seance_list:
                    if (seance.beginning.time() <= beginning.time() <= seance.end.time()) or \
                            (seance.beginning.time() <= end.time() <= seance.end.time()):
                        raise forms.ValidationError(
                            'That time already taken. You can pick another time or another hall')
            return beginning

    class Meta:
        model = models.Seance
        exclude = ('end', 'seats', 'sold_out')
