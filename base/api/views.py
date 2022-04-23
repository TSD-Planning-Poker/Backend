import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room, Task, Deck, Mark
from .serializers import AddMarksSerializer, JoinRoomSerializer, RoomSerializer, DeckSerializer, MarkSerializer, TaskSerialiser2, TaskSerializer, RoomDetailSerializer, DeckDetailSerializer, TaskDetailSerializer, MarkDetailSerializer
from base.api import serializers
from rest_framework import generics, status, viewsets, request
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListCreateAPIView
from django.db import transaction
from django.contrib.auth.models import AbstractUser, User
from django.http import JsonResponse
from django.forms.models import model_to_dict

@api_view(['GET', 'POST'])
def getRoutes(request):
    routes = [
        '/api/rooms',
        '/api/rooms/:id',
        '/api/rooms/<int:pk>/join/<int:id>',
        '/api/room/:id/alltasks',

        '/api/tasks',
        '/api/tasks/:id',
        '/api/tasks/:id/allmarks',
        '/api/tasks/add',

        '/api/marks',
        '/api/marks/add',
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
    serializer_class = JoinRoomSerializer

    @transaction.atomic
    def get(self, request: request.Request, pk, id):

        room = get_object_or_404(Room, pk=pk)
        user = get_object_or_404(User, pk=id)

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

class GetTaskDetail(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

@api_view(['GET', 'POST'])
def getTask(request, pk):
    task = Task.objects.get(id=pk)
    marks = []
    if task:
        marks = list(Mark.objects.filter(task=task).values())
    
    total = 0
    for i in marks:
        total += i['mark']
    if len(marks) > 0:
        total /= len(marks)
        total = round(total, 2)

    dict_obj = model_to_dict( task )

    return JsonResponse(data= {"task": dict_obj, "avarage": total, "marks": marks}, safe=False)


class TaskApiView(generics.GenericAPIView):
    serializer_class = TaskSerialiser2

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = Room.objects.filter(pk=serializer.data['room_id'])

        task = Task.objects.create(
            body = serializer.data['body'],
            room = room.first()
        )
        dict_obj = model_to_dict( task )

        # return Response(json.dumps(task.values()), status=status.HTTP_200_OK)
        return JsonResponse(data= dict_obj, safe=False)



@api_view(['GET'])
def get_tasks_from_room(request, id):
    room = Room.objects.filter(id=id).first()
    if room:
        tasks = list(Task.objects.filter(room=room).values())
    else:
        tasks = []
    
    return JsonResponse(data=tasks, safe=False)

@api_view(['GET'])
def get_marks_from_tasks(request, id):
    task = Task.objects.filter(id=id).first()
    if task:
        marks = list(Mark.objects.filter(task=task).values())
    else:
        marks = []
    

    
    return JsonResponse(data=marks, safe=False)

class AddTask(APIView):
    serializer_class = JoinRoomSerializer

    @transaction.atomic
    def get(self, request: request.Request, pk, id):

        room = get_object_or_404(Room, pk=pk)
        user = get_object_or_404(User, pk=id)

        room.members.add(user)
        room.save()

        serializer_context = {"request": request}
        serializer = self.serializer_class(room, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AddMarks(APIView):
    serializer_class = AddMarksSerializer

    @transaction.atomic
    def get(self, request: request.Request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = get_object_or_404(Task, pk=serializer.data['task_id'])

        mark = Mark.objects.create(
            mark = serializer.data['mark'],  
            task = task
        )

        dict_obj = model_to_dict( mark )

        return JsonResponse(data= dict_obj, safe=False)
# MARK:
class MarkListCreateAPIView(generics.ListCreateAPIView):
    queryset = Mark.objects.all().order_by("id")
    serializer_class = MarkSerializer

@api_view(['GET', 'POST'])
def getMark(request, pk):
    mark = Mark.objects.get(id=pk)
    serializer = MarkDetailSerializer(mark, many=False)
    return Response(serializer.data)