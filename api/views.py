from rest_framework.decorators import api_view
from api.room_views import CustomAPIView
from base.models import Room, Task, Mark, UserStory, VotingHistory
from .serializers import FinaliseStorySerializer, MarkUpdateSerializer, RoomListSerializer, \
    UserStoriesDetailsSerializer, RoomSerializer, MarkSerializer, TaskSerializer, RoomDetailSerializer, \
    MarkDetailSerializer, UserStoriesSerializer
from rest_framework import status, request
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, action
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
import csv
import datetime
import os

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



class StartUserStorySessionApiView(APIView):
    """ List all room """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # serializer_class = UserStoriesSerializer

    def post(self, request, story_id):
        
        try:
            count = 0
            if not request.user.is_superuser:
                raise "You are not Authorised to start session!"

            active_stories = UserStory.objects.filter(current_session=True)
            for stories in active_stories:
                stories.current_session = False
                stories.save()

            story = UserStory.objects.get(id=story_id)
            story.current_session = True
            story.save()

            room = story.room
            members = room.members.all()

            for member in members:
                member_mark = Mark.objects.filter(evaluator=member, user_story=story)
                if member_mark.count() == 0:
                    Mark.objects.create(
                            user_story = story,
                            mark = 0,
                            evaluator = member
                        )
                    
                    VotingHistory.objects.create(
                        mark = 0,
                        user_story = story,
                        evaluator = member,
                        date_evaluated = datetime.datetime.now(),
                        note = "Inital Mark when starting session"
                    )
                else:
                    if member_mark.first().mark > 0:
                        count += 1
            if count == len(members) and story.completed is not True:
                story.evaluated = True
                story.save()

            return Response(
                {
                    "success": True, 
                    "message": "Session started successfully"
                }, status=status.HTTP_200_OK)

        except BaseException as e:
            return Response(
                        {
                            "success": False, 
                            "error": f"Error: {e}"
                        }, status=status.HTTP_400_BAD_REQUEST)


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

    def delete(self, request, story_id):
        try:
            story = UserStory.objects.filter(id=story_id)
            if story.count() == 0:
                raise BaseException("User Story not found")
            story = story.first()
            tasks = story.task_set.all()
            for task in tasks:
                task.delete()
            story.delete()
            return Response({
                "success": True, 
                "message": "User Story Deleted successfully including all Tasks!"
            }, status=200)
        except BaseException as e:
            return Response({
                "success": False,
                "message": f"ERROR: {e}"
            }, status=400)
    

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

        search = request.GET.get('search', None)

        # return instance.members.filter(pk=self.context.get('request').user).exists()

        if search:
            print('--------searching--------', search)
            rooms = Room.objects.filter(members__in=str(request.user.pk),  name__contains=search)
        else:
            rooms = Room.objects.filter(members__in=str(request.user.pk))

        data = RoomListSerializer(rooms, many=True).data
        
        return JsonResponse(data=data, safe=False)

    def post(self, request):
            """
            We create a new room object, and then we return a dictionary representation of that room object

            :param request: The request object
            :return: A JsonResponse object.
            """
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            try: 
                room = Room.objects.create(
                    name=serializer.data['name'],
                    description=serializer.data['description'],
                    host=request.user
                )
                room.save()

            except BaseException as e:
                return Response(data={
                        "success": False,
                        "message": f"ERROR: {e}",
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            room_dict = model_to_dict(room)
            room.members.add(request.user.id)

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
        if request.user.is_superuser:
            marks = list(Mark.objects.filter(user_story=user_story).values("id", "mark", "evaluator__username", "evaluator__email",))
        else:
            if user_story.completed:
                marks = list(Mark.objects.filter(user_story=user_story).values("id", "mark", "evaluator__username", "evaluator__email",))
            else:
                marks = list(Mark.objects.filter(user_story=user_story).values("id", "evaluator__username", "evaluator__email",))
    
        for mark in marks:
            if mark['evaluator__username'] == request.user.username:
                mark['mark'] = Mark.objects.get(user_story=user_story, evaluator=request.user).mark
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
class MarkListAPIView(CustomAPIView):
    """
    List all marks 
    Method: Get
    """
    serializer_class = MarkSerializer

    def get(self, request: request.Request):
        if request.user.is_superuser:
            marks = Mark.objects.all().values("id", "mark", "user_story", "user_story__room__name","user_story__room__id", "user_story__title","evaluator", "evaluator__username")
        else:
            marks = Mark.objects.filter(evaluator=request.user).values("id", "mark", "user_story", "user_story__room__name","user_story__room__id", "user_story__title","evaluator", "evaluator__username")
        return Response(data={
                        "success": True,
                        "message": "Successfully fetched marks",
                        "data": marks
                    }, status=status.HTTP_200_OK)
        

    def post(self, request: request.Request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=False)
            user_story_to_evaluate = UserStory.objects.filter(id=serializer.data['user_story'])

            if not user_story_to_evaluate:
                raise BaseException('Canot not find the user story to be evaluated!')                

            search = Mark.objects.filter(evaluator=request.user, user_story = user_story_to_evaluate )
            if search.count() > 0:
                raise BaseException('User story is already evaluated by the user!')

            mark = Mark.objects.create(
                user_story = user_story_to_evaluate,
                mark = float(str(serializer.data['mark'])),
                evaluator = request.user
            )

            mark = model_to_dict(mark)
            return Response(data={
                        "success": True,
                        "message": "Successfully evaluated a story",
                        "data": mark
                    }, status=status.HTTP_200_OK)
        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": "Failed to evaluate a user story!",
                    "error": f'{e}'
                }, status=status.HTTP_400_BAD_REQUEST)


class FinaliseUSerStoryApiView(CustomAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = FinaliseStorySerializer

    def post(self, request, story_id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if not request.user.is_superuser:
                raise BaseException('You are not authorised to finilise a user story!')
            story = UserStory.objects.get(id=story_id)
            story.final_mark = serializer.data['final_mark']
            story.completed = True
            story.evaluated = True
            story.save()
            return Response(data={
                        "success": True,
                        "message": "Successfully finalised Story!",
                    }, status=status.HTTP_200_OK)
        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": "Story Cound not be finalised",
                    "error": f'{e}'
                }, status=status.HTTP_400_BAD_REQUEST)

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


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateMark(request, pk):
    """
    Get mark details 
    Method: GET
    Accepts: mark_id
    """
    try:
        serializer = MarkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mark = Mark.objects.get(id=pk)
        
        if request.user == mark.evaluator:
            mark.mark = serializer.data['mark']
            mark.save()
            VotingHistory.objects.create(
                        mark = serializer.data['mark'],
                        user_story = mark.user_story,
                        evaluator = mark.evaluator,
                        date_evaluated = datetime.datetime.now(),
                        note = "Updated Mark"
                    )
        else:
            raise BaseException('You are not authorised to update this mark')

        mark = model_to_dict(mark)
        return Response(data={
                        "success": True,
                        "message": "Successfully updated a mark",
                        "data": mark
                    }, status=status.HTTP_200_OK)

    except BaseException as e:
        return Response(data={
                        "success": False,
                        "message": f"{e}",
                        "error": "Please contact the admin." 
                    }, status=status.HTTP_400_BAD_REQUEST)   



class ExportCSV_withDelimeter(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, delimeter):
        """
        Export csv file for Jira with given delimeter
        Method: GET
        Accepts: delimeter
        """
        try:
            stories = UserStory.objects.all().only('created_at','description','created_by')
            delimtr = delimeter

            # response = HttpResponse(content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="export.csv"'
            # writer = csv.writer(response)
            if not os.path.exists("staticfiles/tmp"):
                os.makedirs("staticfiles/tmp")

            writer = open("staticfiles/tmp/tmpExport.csv", 'w', newline='')
            writer = csv.writer(writer)

            header = ('Issue Type','Summary','Reporter','Created')
            header = delimtr.join(header)
            writer.writerow([header])

            for story in stories:
                user = User.objects.get(id=story.created_by_id)
                row = ('Story', story.description, user.username, story.created_at.strftime("%d/%b/%y"))
                row = delimtr.join(row)
                writer.writerow([row])
            
            return Response(data={
                            "success": True,
                            "exportPath": f"tmp/tmpExport.csv",
                        }, status=status.HTTP_200_OK)

        except BaseException as e:
            return Response(data={
                "success": False,
                "message": "Failed to export file",
                "error": f'{e}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExportCSV_withDelimeterForRoom(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, delimeter, pk):
        """
        Export csv file for Jira with given delimeter for specific room
        Method: GET
        Accepts: delimeter_roomId
        """
        try:
            room = Room.objects.get(pk=pk)
            stories = UserStory.objects.filter(room=room).only('created_at','description','created_by')
            delimtr = delimeter

            # response = HttpResponse(content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="export.csv"'
            # writer = csv.writer(response)
            if not os.path.exists("staticfiles/tmp"):
                os.makedirs("staticfiles/tmp")

            writer = open("staticfiles/tmp/tmpExport.csv", 'w', newline='')
            writer = csv.writer(writer)

            header = ('Issue Type','Summary','Reporter','Created')
            header = delimtr.join(header)
            writer.writerow([header])

            for story in stories:
                user = User.objects.get(id=story.created_by_id)
                row = ('Story', story.description, user.username, story.created_at.strftime("%d/%b/%y"))
                row = delimtr.join(row)
                writer.writerow([row])
            
            return Response(data={
                            "success": True,
                            "exportPath": f"tmp/tmpExport.csv",
                        }, status=status.HTTP_200_OK)

        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": f'Failed to export file for {pk} room id',
                    "error": f'{e}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


FILE_STORAGE = FileSystemStorage(location='tmp/')
class ImportCSV_withDelimeter(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # @action(detail=False, methods='POST')
    def post(self, request, delimeter, pk):
        """
        Import csv file from Jira with given delimeter for specific room
        Method: POST
        Accepts: delimeter_roomId
        """
        try:
            file = request.FILES["file"]
            delimtr = str(delimeter)

            content = file.read()
            file_content = ContentFile(content)
            file_name = FILE_STORAGE.save("_tmp.csv", file_content)
            tmp_file = FILE_STORAGE.path(file_name)

            csv_file = open(tmp_file, errors="ignore")
            reader = csv.reader(csv_file, delimiter=delimtr)
            # next(reader) # header row skipped

            stories_list = []
            get_fields = []
            description = ""
            created_by = ""
            created_at = ""
            for id, row in enumerate(reader):
                if id == 0:
                    for i, f in enumerate(row):
                        if f == "Issue Type":
                            get_fields.append(i)
                        elif f == "Summary":
                            get_fields.append(i)
                        elif f == "Reporter":
                            get_fields.append(i)
                        elif f == "Created":
                            get_fields.append(i)
                else:
                    if row[get_fields[0]] == "Story":
                        description = row[get_fields[1]] 
                        created_by = row[get_fields[2]] 
                        created_at = row[get_fields[3]] 
                        stories_list.append(
                            UserStory(
                                # room = Room.objects.get(host=request.user),
                                room = Room.objects.get(pk=pk),
                                title = f"Story {id}: {description[:10]}",
                                description = description,
                                created_by = request.user,
                                created_at = created_at,
                                updated_at = datetime.date.today()
                            )
                        )
            UserStory.objects.bulk_create(stories_list)

            return Response(data={
                            "success": True,
                            "message": "Successfully uploaded data",
                        }, status=status.HTTP_200_OK)
        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": "Failed to upload file",
                    "error": f'{e}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


 
# UPDATE PASSWORD:
class ChangePassword(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        
        if request.user.is_superuser:
            user = User.objects.get(id=pk)
            user.set_password(request.data['password'])
            user.save()

            return Response(data={
                            "success": True,
                            "message": "Successfully changed password",
                        }, status=status.HTTP_200_OK)
        return Response(data={
                            "success": False,
                            "message": "Only admin user can change password",
                        }, status=status.HTTP_401_UNAUTHORIZED)

class VotingHistorys(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, story_id):

        try:

            story = UserStory.objects.filter(id=story_id)
            if story.count() == 0:
                raise BaseException("User Story could not be found")

            story = story.first()

            voting_histories = story.votinghistory_set.all().values()
            
            return Response(data={
                "success": True,
                "data": voting_histories
            },)

        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": f"ERROR: {e}",
                }, status=status.HTTP_400_BAD_REQUEST)
