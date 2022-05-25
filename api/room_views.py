from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status, viewsets, request
from django.contrib.auth.models import AbstractUser, User
from api.serializers import InvitationsSerializer
from api.utils import generate_unique_code

from base.models import Invitation, Room

class CustomAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    

class RoomInvitations(CustomAPIView):

    serializer_class = InvitationsSerializer

    def check_if_already_a_member(self, room, invited_user):
        # Check if the user is a member of the quested group
        search = room.members.filter(id=invited_user.id)
        inv = Invitation.objects.filter(room=room, to_user=invited_user)
        if search.count() > 0:
            raise BaseException("User is already a member of the room")
        elif inv.count() > 0:
            raise BaseException(f"Pendding invitation already exist for the user with invitation code = {inv.first().code}")


    def get(self, request):
        """
        It returns a list of all the invitations sent to the current user
        
        :param request: The request object
        :return: A list of dictionaries.
        """
        
        invitations = Invitation.objects.filter(to_user=request.user, accepted=False).values("id", "from_user__username", 
        "room_id__name", "accepted", "created_at", "code")

        return Response(data=invitations, status=status.HTTP_200_OK)

    def post(self, request):
        """
        It creates an invitation object and returns it to the user
        
        :param request: The request object
        """
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            room = Room.objects.get(id=serializer.data['room'])
            invitation_to_user = User.objects.get(id=serializer.data['to_user'])
            
            if room.host == request.user:
                self.check_if_already_a_member(room, invitation_to_user)
                invitation = Invitation.objects.create(
                    from_user = request.user,
                    to_user = invitation_to_user,
                    accepted = False,
                    room = room,
                    code = generate_unique_code()
                )
                inv = model_to_dict(invitation)

                return Response(data={
                    "success": True,
                    "message": "invitation sent successfully",
                    "data": inv
                }, status=status.HTTP_200_OK)

        except BaseException as e:
            return Response(data={
                    "success": False,
                    "message": "Failed to send invitation, Please try again!",
                    "error": f'{e}'
                }, status=status.HTTP_400_BAD_REQUEST)



class AcceptInviteApiView(CustomAPIView):

    def post(self, request: request.Request, invitation_code):
        """
        It checks if the invitation code is valid, if it is, it checks if the user requesting the
        invitation code is the same user the invitation code was sent to, if it is, it accepts the
        invitation and joins the user to the room
        
        :param request: request.Request: This is the request object that is sent to the server
        :type request: request.Request
        :param invitation_code: The invitation code that the user is trying to use to join the room
        :return: A response object is being returned.
        """
        try:
            invitation = Invitation.objects.get(code=invitation_code)
            room = invitation.room
            user = request.user

            # Check if the invitation is alredy been accepted
            if invitation.accepted:
                raise BaseException("Invitation has already been accepted")
            
            # Check if the user is requesting their own invitation code
            if invitation.to_user == user:
                invitation.accepted = True
                invitation.save()
                
                # Join user to the room
                room.members.add(user)
                room.save()

                return Response(
                    {
                        "success": True, 
                        "room_joined": room.id, 
                        "message": "you have successfully joined the room"
                    }, status=status.HTTP_200_OK)
            else:
                raise BaseException("You are not allowed to use this invitation code!")
                  
        except BaseException as e:
            return Response(
                    {
                        "success": False, 
                        "message": "Enable to process your request please try again!",
                        "error": f'{e}'
                    }, status=status.HTTP_200_OK)
        

