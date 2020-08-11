from rest_framework import serializers
from movies import models
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    ticket_set = serializers.HyperlinkedRelatedField(many=True, view_name='user_tickets_detail', read_only=True)

    class Meta:
        model = User
        fields = ('username', 'ticket_set')


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Film
        fields = ('__all__')


class SeanceSerializer(serializers.ModelSerializer):
    # film = FilmSerializer()

    class Meta:
        model = models.Seance
        fields = ('__all__')


class TicketSerializer(serializers.ModelSerializer):
    # seance = SeanceSerializer()

    class Meta:
        model = models.Ticket
        fields = ('__all__')

# class TicketSerializer(serializers.Modelserialezer):
#
#
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return models.Ticket.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Snippet` instance, given the validated data.
#         """
#         instance.title = validated_data.get('title', instance.title)
#         instance.code = validated_data.get('code', instance.code)
#         instance.linenos = validated_data.get('linenos', instance.linenos)
#         instance.language = validated_data.get('language', instance.language)
#         instance.style = validated_data.get('style', instance.style)
#         instance.save()
#         return instance