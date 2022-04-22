from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room, Task, Deck, Mark
from .serializers import RoomSerializer, DeckSerializer, MarkSerializer, TaskSerializer, RoomDetailSerializer, DeckDetailSerializer, TaskDetailSerializer, MarkDetailSerializer
from base.api import serializers
from rest_framework import generics, status, viewsets, request
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListCreateAPIView
from django.db import transaction


@api_view(['GET', 'POST'])
def getRoutes(request):
    routes = [
        '/api',
        '/api/rooms',
        '/api/rooms/:id',
        '/api/rooms/:id/create_deck', # TODO
        '/api/room/:id/join',
        '/api/decks',
        '/api/decks/:id',
        '/api/decks/:id/cerate_task', # TODO
        '/api/tasks',
        '/api/tasks/:id',
        '/api/marks',
        '/api/marks/:id',
    ]
    return Response(routes)


# ROOM:
@api_view(['GET', 'POST'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomDetailSerializer(room, many=False)
    return Response(serializer.data)

class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all().order_by("id")
    serializer_class = RoomSerializer

class JoinRoomAPIView(APIView):
    serializer_class = RoomSerializer

    @transaction.atomic
    def post(self, request: request.Request, pk):
        room = get_object_or_404(Room, pk=pk)
        user = request.user

        room.members.add(user)
        room.save()

        serializer_context = {"request": request}
        serializer = self.serializer_class(room, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)



# DECK:
class DeckListCreateAPIView(generics.ListCreateAPIView):
    queryset = Deck.objects.all().order_by("id")
    serializer_class = DeckSerializer

@api_view(['GET', 'POST'])
def getDeck(request, pk):
    deck = Deck.objects.get(id=pk)
    serializer = DeckDetailSerializer(deck, many=False)
    return Response(serializer.data)



# TASK:
class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all().order_by("id")
    serializer_class = TaskSerializer

@api_view(['GET', 'POST'])
def getTask(request, pk):
    task = Task.objects.get(id=pk)
    serializer = TaskDetailSerializer(task, many=False)
    return Response(serializer.data)



# MARK:
class MarkListCreateAPIView(generics.ListCreateAPIView):
    queryset = Mark.objects.all().order_by("id")
    serializer_class = MarkSerializer

@api_view(['GET', 'POST'])
def getMark(request, pk):
    mark = Mark.objects.get(id=pk)
    serializer = MarkDetailSerializer(mark, many=False)
    return Response(serializer.data)