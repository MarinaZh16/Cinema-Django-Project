from rest_framework import serializers
from movies import models
from user.models import User
import datetime
from django.utils import timezone


class CinemaSerializer(serializers.HyperlinkedModelSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    ticket_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='user_tickets_detail', read_only=True
    )

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff', 'ticket_set']
        read_only_fields = ['username', 'email']


# class CreateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('email', 'username', 'password')
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def create(self, validated_data):
#         user = User(
#             email=validated_data['email'],
#             username=validated_data['username']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user

class HallSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Hall
        fields = '__all__'


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Film
        exclude = ['is_deleted']


class SeanceSerializer(serializers.ModelSerializer):


    class Meta:
        model = models.Seance
        fields = ('film', 'hall', 'beginning', 'price')

    def validate(self, data):
        beginning = data['beginning']
        film = models.Film.objects.get(title=data['film'])
        if datetime.date.today() > film.end_show:
            raise serializers.ValidationError('This movie has expired!')
        elif film.start_show > beginning.date() or beginning.date() > film.end_show:
            raise serializers.ValidationError('That date is out of range. Pick date between %s - %s' %
                                                (film.start_show, film.end_show))
        elif beginning < timezone.now():
            raise serializers.ValidationError('This time has passed')
        else:
            seance_list = models.Seance.objects.filter(hall=data['hall'],
                                                       beginning__date=beginning.date())
            if seance_list:
                end = beginning + film.duration
                for seance in seance_list:
                    if (seance.beginning.time() <= beginning.time() <= seance.end.time()) or \
                            (seance.beginning.time() <= end.time() <= seance.end.time()):
                        raise serializers.ValidationError(
                            'That time already taken. You can pick another time or another hall')
            return data


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ticket
        fields = ['seance', 'row', 'seat', 'user']
        read_only_fields = ['user']

    def validate(self, data):
        seance = data['seance']
        if seance.beginning < timezone.now():
            raise serializers.ValidationError('Time is up! You can not byu ticket on this seance!')
        else:
            seat = data['seat']
            row = data['row']
            ticket_check = models.Ticket.objects.filter(seance=seance, row=row, seat=seat)
            if seance.seats == 0:
                raise serializers.ValidationError('Sorry, all seats already taken! Pick another seance!')
            elif ticket_check:
                serializers.ValidationError('seat %s in row %s is already taken! Pick another one!' % (seat, row))
            elif row > seance.hall.row or seat > seance.hall.seat:
                raise serializers.ValidationError('You can not chose this seat.'
                                                  ' In request hall %s rows and %s seats'
                                                  % (seance.hall.row, seance.hall.seat))
            else:
                seance.seats -= 1
                return data
