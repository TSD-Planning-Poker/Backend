from http import HTTPStatus
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.serializers import UserProfileSerializer
from django.forms.models import model_to_dict
from django.contrib.auth.models import User

from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Log out users
    """
    token = Token.objects.get(user=request.user)
    key = token.key
    token.delete()
    return Response(data={"token": key}, status=HTTPStatus.ACCEPTED)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def allusers_view(request):
    """
    Fetch all users
    """
    if request.user.is_superuser:
        users = User.objects.all().values("id", "username", "is_staff", "is_superuser", "email")
        return Response(data=users, status=HTTPStatus.ACCEPTED)
        
    else:
        return Response(status=HTTPStatus.FORBIDDEN)


class ProfileApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        user = User.objects.filter(id=request.user.id).values("username", "first_name", "last_name", "email", "date_joined").first()
        return Response(data=user, status=200)

    def clean_userdata(self):
        del self.profile_user['id']
        del self.profile_user['password']
        del self.profile_user['is_superuser']
        del self.profile_user['is_active']
        del self.profile_user['is_staff']
        del self.profile_user['groups']
        del self.profile_user['user_permissions']


    def post(self, request):
        self.profile_user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.profile_user.username = serializer.data['username']
            self.profile_user.first_name = serializer.data['first_name']
            self.profile_user.last_name = serializer.data['last_name']
            self.profile_user.email = serializer.data['email']
            self.profile_user.save()
            
            # Change user model to dict object (desrialize)
            self.profile_user = model_to_dict(self.profile_user)

            # Clean user sensitive data
            self.clean_userdata()

            return Response(data=self.profile_user, status=200)
        else:
            return Response(data={"error": "Wrong Input, Please try again"}, status=400)



