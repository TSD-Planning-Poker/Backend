from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer
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
        '/api/room/:id/join'
    ]
    return Response(routes)


# @api_view(['GET', 'POST'])
# def getRooms(request):
#     rooms = Room.objects.all()
#     serializer = RoomSerializer(rooms, many=True)
#     return Response(serializer.data)


@api_view(['GET', 'POST'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)


class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all().order_by("id")
    serializer_class = RoomSerializer

# class RoomDetailListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Room.objects.all().order_by("id")
#     serializer_class = RoomSerializer

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
