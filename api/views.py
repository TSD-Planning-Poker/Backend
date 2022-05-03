import json
from unicodedata import name
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.room_views import CustomAPIView
from base.models import Room, Task, Mark, UserStory
from .serializers import UserStoriesDetailsSerializer, RoomSerializer, MarkSerializer, TaskSerializer, RoomDetailSerializer, MarkDetailSerializer, UserStoriesSerializer
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


class RoomsUpdateAndDetailsView(APIView):
    """ List all room """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = RoomSerializer

    def get(self, request, pk):
        """
        It gets a room with the given id, serializes it, and returns it

        :param request: The request object is used to get the request data
        :param pk: The primary key of the room we want to retrieve
        :return: The room object is being returned.
        """
        room = Room.objects.get(id=pk)
        serializer = RoomDetailSerializer(room, many=False)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        If the room exists, update the room's name and description, and return the room's dictionary

        :param request: The request object
        :param pk: The primary key of the room to be updated
        :return: A JsonResponse object is being returned.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = Room.objects.filter(id=pk)

        if room.count() > 0:
            room = room.first()
            room.name = serializer.data['name']
            room.description = serializer.data['description']
            room.save()
            room_dict = model_to_dict(room)
            return JsonResponse(data=room_dict, safe=False)
        else:
            return Response("Resource not found", status=status.HTTP_200_OK)


class UserStoriesApiView(APIView):
    """ List all room """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserStoriesSerializer

    def get(self, request):
        """
        It returns a list of all the values in the UserStories table

        :param request: The request object is a standard Django request object
        :return: The list of all the values in the UserStories table.
        """
        room = list(UserStory.objects.all().values())
        return Response(room)

    def post(self, request):
        """
        It creates a new UserStory object and returns a JsonResponse with the data of the newly created
        object

        :param request: The request object
        :return: The serializer.data is being returned.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        story = UserStory.objects.create(
            room = Room.objects.get(id=serializer.data['room']),
            title=serializer.data['title'],
            description=serializer.data['description'],
            created_by=request.user
        )

        sotry_obj = model_to_dict(story)
        return JsonResponse(data=sotry_obj, safe=False)


class UserStoriesUpdateAndDetailsApiView(APIView):
    """ List all room """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserStoriesDetailsSerializer

    def get(self, request, story_id):
        """
        It takes a request and a story_id, and returns a response with the story if it exists, or a
        response with an error message if it doesn't

        :param request: The request object that was sent to the view
        :param story_id: The id of the story you want to get
        :return: The user story is being returned.
        """
        room = UserStory.objects.filter(id=story_id)
        if room.count() > 0:
            room = room.values().first()
            return Response(room)
        else:
            return Response("User story not found", status=400)

    def put(self, request, story_id):
        """
        It takes a request and a story_id, validates the request, gets the story, updates the story, and
        returns the updated story

        :param request: The request object is the first parameter to the view. It contains the request
        data, including the request body, query parameters, and headers
        :param story_id: The id of the story you want to update
        :return: The response is a JSON object with the updated story.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        story = UserStory.objects.get(id=story_id)

        if story:
            story.title = serializer.data['title']
            story.description = serializer.data['description']
            story.save()
            sotry_obj = model_to_dict(story)
            return JsonResponse(data=sotry_obj, safe=False)
        else:
            return Response("User story not found", status=400)


class RoomListCreateAPIView(APIView):
    """ List all room """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = RoomSerializer

    def get(self, request):
        """
        It returns a list of all the rooms in the database, ordered by their id, in JSON format

        :param request: The request object
        :return: A list of all the rooms in the database.
        """
        rooms = list(Room.objects.all().order_by("id").values())
        return JsonResponse(data=rooms, safe=False)

    def post(self, request):
        """
        We create a new room object, and then we return a dictionary representation of that room object

        :param request: The request object
        :return: A JsonResponse object.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = Room.objects.create(
            name=serializer.data['name'],
            description=serializer.data['description'],
            host=request.user,
        )
        # room.save()
        room_dict = model_to_dict(room)

        return JsonResponse(data=room_dict, safe=False)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def leave_room(request: request.Request, pk):
    try:
        room = get_object_or_404(Room, pk=pk)
        user = request.user

        # Check if the user is a member of the quested group
        search = room.members.filter(id=user.id)
        if search.count() == 0:
            raise BaseException("You are not a member of this room, Please check the admin of this room")
        
        # Remove user from the room
        room.members.remove(user)
        room.save()

        return Response(
            {
                "success": True, 
                "room_joined": room.id, 
                "message": "you have successfully removed from the room"
            }, status=status.HTTP_200_OK)
    except BaseException as e:
        return Response(
            {
                "success": False, 
                "message": "Unable to process your request please try again",
                "error": f'{e}'
            }
            , status=status.HTTP_400_BAD_REQUEST)


# TASK:
class TaskListAPIView(CustomAPIView):
    """
    List all tasks
    Method: GET
    """
    
    serializer_class = TaskSerializer

    def get(self, request):
        tasks = list(Task.objects.all().values())
        return JsonResponse(data=tasks, safe=False)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = Task.objects.create(
            title=serializer.data['title'],
            description=serializer.data['description'],
            user_story=UserStory.objects.get(id=serializer.data['user_story']),
            created_by = request.user
        )
        task_dict = model_to_dict(task)

        return JsonResponse(data=task_dict, safe=False)


class TasksDetailsAndUpdateApiView(CustomAPIView):

    def get(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
            dict_obj = model_to_dict(task)
            return JsonResponse(data=dict_obj, safe=False)
        except BaseException as e:
            return JsonResponse(data={"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
            task.delete()
            return Response(data={
                        "success": True,
                        "message": "Successfully delete task",
                    }, status=status.HTTP_200_OK)
        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": "Task does not exist!",
                    "error": f'{e}'
                }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_userstories_from_room(request, id):
    """
    List stories in a room
    Method: Get
    Accepts: room_id
    """
    room = Room.objects.filter(id=id).first()
    if room:
        user_stories = list(UserStory.objects.filter(room=room).values())
    else:
        user_stories = []

    return JsonResponse(data=user_stories, safe=False)


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
def get_marks_from_userstories(request, id):
    """
    List  marks assigned for a task
    Metod: Get
    Accepts: task_id
    """
    user_story = UserStory.objects.filter(id=id).first()
    if user_story:
        marks = list(Mark.objects.filter(user_story=user_story).values())
    else:
        marks = []
    return JsonResponse(data=marks, safe=False)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_tasks_in_story(request, id):
    """
    It takes a task id, finds the task, and returns a list of all the stories associated with that task

    :param request: The request object
    :param id: the id of the task
    :return: A list of dictionaries.
    """
    story = UserStory.objects.filter(id=id).first()
    if story:
        tasks = list(story.task_set.all().values())
    else:
        tasks = []
    return JsonResponse(data=tasks, safe=False)


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
