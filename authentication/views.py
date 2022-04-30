from http import HTTPStatus
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from rest_framework.response import Response

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