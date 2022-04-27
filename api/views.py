import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room, Task, Deck, Mark
from .serializers import AddMarksSerializer, JoinRoomSerializer, RoomSerializer, MarkSerializer, TaskSerialiser2, TaskSerializer, RoomDetailSerializer, TaskDetailSerializer, MarkDetailSerializer
from api import serializers
from rest_framework import generics, status, viewsets, request
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404, ListCreateAPIView
from django.db import transaction
from django.contrib.auth.models import AbstractUser, User
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes

@api_view(['GET'])
def getRoutes(request):
    """
    Get all routes temp view
    """
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
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getRoom(request, pk):
    """ Get Room details """
    room = Room.objects.get(id=pk)
    serializer = RoomDetailSerializer(room, many=False)
    return Response(serializer.data)

class RoomListCreateAPIView(generics.ListCreateAPIView):
    """ List all room """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Room.objects.all().order_by("id")
    serializer_class = RoomSerializer

class JoinRoomAPIView(APIView):
    """ 
    Join a specific room 
    Method: GET
    Accepts: pk(room_id), id(user_id)
    """
    serializer_class = JoinRoomSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request: request.Request, pk, id):

        room = get_object_or_404(Room, pk=pk)
        user = get_object_or_404(User, pk=id)

        room.members.add(user)
        room.save()

        serializer_context = {"request": request}
        serializer = self.serializer_class(room, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)


# TASK:
class TaskListAPIView(generics.ListCreateAPIView):
    """
    List all tasks
    Method: GET
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all().order_by("id")
    serializer_class = TaskSerializer

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getTask(request, pk):
    """ 
    Get task details with marks and average mark
    Method: Get
    Accepts: (int) Task_id
    """
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


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_tasks_from_room(request, id):
    """
    List tasks in a room
    Method: Get
    Accepts: room_id
    """
    room = Room.objects.filter(id=id).first()
    if room:
        tasks = list(Task.objects.filter(room=room).values())
    else:
        tasks = []
    
    return JsonResponse(data=tasks, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_users_from_room(request, id):
    """
    List users in a room
    Method: Get
    Accepts: room_id
    """
    room = Room.objects.filter(id=id).first()
    if room:
        members = list(room.members.all().values())

    else:
        members = []
    
    return JsonResponse(data=members, safe=False)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_marks_from_tasks(request, id):
    """
    List  marks assigned for a task
    Metod: Get
    Accepts: task_id
    """
    task = Task.objects.filter(id=id).first()
    if task:
        marks = list(Mark.objects.filter(task=task).values())
    else:
        marks = []
    return JsonResponse(data=marks, safe=False)


# MARK:
class MarkListAPIView(generics.ListCreateAPIView):
    """
    List all marks 
    Method: Get
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Mark.objects.all().order_by("id")
    serializer_class = MarkSerializer


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getMark(request, pk):
    """
    Get mark details 
    Method: GET
    Accepts: mark_id
    """
    mark = Mark.objects.get(id=pk)
    serializer = MarkDetailSerializer(mark, many=False)
    return Response(serializer.data)