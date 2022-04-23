from dataclasses import field
from rest_framework.serializers import ModelSerializer, StringRelatedField, SerializerMethodField, JSONField, Serializer
from base.models import Room, Deck, Task, User, Mark
from django.db import models
from django.http import JsonResponse
from rest_framework import serializers
from django.http import HttpResponse
from rest_framework.response import Response
# from rest_framework.decorators import action


class StringLookupField(StringRelatedField):
    def __init__(self, model: models.Model, field: str, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.field = field

    def to_internal_value(self, data):
        obj = self.model.objects.filter(**{self.field: data}).first()
        return obj.id


# ROOM:
class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        exclude = ["updated", "created"]

class JoinRoomSerializer(Serializer):
    room = Room
    user = User


class AddMarksSerializer(Serializer):
    mark = serializers.FloatField()
    task_id = serializers.IntegerField()

class TaskSerialiser2(Serializer):
    room_id = serializers.CharField()
    body = serializers.CharField()

class RoomDetailSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

    members = StringLookupField(User, "username", many=True)
    deck = SerializerMethodField(read_only=True)

    def get_deck(self, instance):
        deck = Deck.objects.filter(room=instance.pk).values('id')
        if deck.count() > 0:
            return deck
        else:
            return []

    def join_room(self, instance, user):
        try: 
            instance.members.add(user)
            return True
        except Exception as e:
            print(e)
            return False
        

        



# DECK:
class DeckSerializer(ModelSerializer):
    class Meta:
        model = Deck
        exclude = ["updated", "created"]

class DeckDetailSerializer(ModelSerializer):
    class Meta:
        model = Deck
        fields = "__all__"

    tasks = SerializerMethodField(read_only=True)

    def get_tasks(self, instance):
        tasks = Task.objects.filter(deck=instance.pk).values("id", "user_id", "body")
        print(tasks)
        return tasks
        


# TASK:
class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        exclude = ["updated", "created"]

class TaskDetailSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"



# MARK:
class MarkSerializer(ModelSerializer):
    class Meta:
        model = Mark
        exclude = ["updated", "created"]

class MarkDetailSerializer(ModelSerializer):
    class Meta:
        model = Mark
        fields = "__all__"
