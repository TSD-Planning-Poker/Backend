from rest_framework.serializers import ModelSerializer
from base.models import Room, Deck, Task, User


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class DeckSerializer(ModelSerializer):
    class Meta:
        model = Deck
        fields = '__all__'


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
