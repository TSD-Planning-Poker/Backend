from django.urls import path
from . import views
from base.api.views import AddMarks, RoomListCreateAPIView, JoinRoomAPIView, MarkListCreateAPIView, DeckListCreateAPIView, TaskApiView, TaskListCreateAPIView, get_marks_from_tasks, get_tasks_from_room


urlpatterns = [
    path('', views.getRoutes),

    path('rooms/', RoomListCreateAPIView.as_view(), name="room-list"),
    path('rooms/<int:id>/alltasks/', get_tasks_from_room, name="room-alltasks"),
    path('rooms/<int:pk>/', views.getRoom, name="room-detail"),
    path('rooms/<int:pk>/join/<int:id>', JoinRoomAPIView.as_view(), name="room-join"),

    # path('decks/', DeckListCreateAPIView.as_view(), name="deck-list"),
    # path('decks/<int:pk>/', views.getDeck, name="deck-detail"),

    path('tasks/<int:id>/allmarks', get_marks_from_tasks, name="mark-listmark"),
    path('tasks/add', TaskApiView.as_view(), name="task-add"),
    path('tasks/', TaskListCreateAPIView.as_view(), name="task-list"),
    path('tasks/<int:pk>/', views.getTask, name="task-detail"),

    path('marks/add', AddMarks.as_view(), name="mark-add"),
    path('marks/', MarkListCreateAPIView.as_view(), name="mark-list"),
    path('marks/<int:pk>/', views.getMark, name="mark-detail"),
]
