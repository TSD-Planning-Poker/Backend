from django.urls import path
from . import views
from base.api.views import RoomListCreateAPIView, JoinRoomAPIView, MarkListCreateAPIView, DeckListCreateAPIView, TaskListCreateAPIView


urlpatterns = [
    path('', views.getRoutes),

    path('rooms/', RoomListCreateAPIView.as_view(), name="room-list"),
    path('rooms/<int:pk>/', views.getRoom, name="room-detail"),
    path('rooms/<int:pk>/join', JoinRoomAPIView.as_view(), name="room-join"),

    path('decks/', DeckListCreateAPIView.as_view(), name="deck-list"),
    path('decks/<int:pk>/', views.getDeck, name="deck-detail"),

    path('tasks/', TaskListCreateAPIView.as_view(), name="task-list"),
    path('tasks/<int:pk>/', views.getTask, name="task-detail"),

    path('marks/', MarkListCreateAPIView.as_view(), name="mark-list"),
    path('marks/<int:pk>/', views.getMark, name="mark-detail"),
]
