from django.urls import path
from . import views
from base.api.views import RoomListCreateAPIView, JoinRoomAPIView


urlpatterns = [
    path('', views.getRoutes),
    # path('rooms/', views.getRooms),
    path('rooms/', RoomListCreateAPIView.as_view(), name="room-list"),
    path('rooms/<int:pk>/', views.getRoom, name="room-detail"),
    path('rooms/<int:pk>/join', JoinRoomAPIView.as_view(), name="room-join"),
]
