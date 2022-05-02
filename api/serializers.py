from dataclasses import field
from rest_framework.serializers import ModelSerializer, StringRelatedField, SerializerMethodField, JSONField, Serializer
from base.models import Room, Deck, Task, User, Mark, UserStories
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
        exclude = ["updated_at", "created_at", "members"]


class UserStoriesSerializer(ModelSerializer):
    class Meta:
        model = UserStories
        exclude = ["updated_at", "created_at", "created_by"]

class UserStoriesDetailsSerializer(ModelSerializer):
    class Meta:
        model = UserStories
        exclude = ["updated_at", "created_at", "created_by", "related_task"]

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
    # deck = SerializerMethodField(read_only=True)

    def join_room(self, instance, user):
        try: 
            instance.members.add(user)
            return True
        except Exception as e:
            print(e)
            return False

# TASK:
class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        exclude = ["updated_at", "created_at"]

class TaskDetailSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

# MARK:
class MarkSerializer(ModelSerializer):
    class Meta:
        model = Mark
        exclude = ["updated_at", "created_at"]

class MarkDetailSerializer(ModelSerializer):
    class Meta:
        model = Mark
        fields = "__all__"
