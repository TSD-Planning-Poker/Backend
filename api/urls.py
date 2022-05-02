from django.urls import path
from . import views
from .views import leave_room, get_stories_in_task, UserStoriesUpdateAndDetailsApiView, UserStoriesApiView, RoomsUpdateAndDetailsView, RoomListCreateAPIView, JoinRoomAPIView, MarkListAPIView, TaskListAPIView, TaskListAPIView, get_users_from_room, get_marks_from_tasks, get_tasks_from_room


urlpatterns = [
    path('rooms/', RoomListCreateAPIView.as_view(), name="room-list"),
    path('rooms/<int:id>/alltasks/', get_tasks_from_room, name="room-alltasks"),
    path('rooms/<int:id>/allusers/', get_users_from_room, name="room-alltasks"),
    path('rooms/<int:pk>/', RoomsUpdateAndDetailsView.as_view(), name="room-detail"),
    path('rooms/<int:pk>/join/', JoinRoomAPIView.as_view(), name="room-join"),
    path('rooms/<int:pk>/leave/', leave_room, name="room-join"),

    path('tasks/<int:id>/allmarks', get_marks_from_tasks, name="mark-listmark"),
    path('tasks/<int:id>/stories', get_stories_in_task, name="stories_in_task"),
    path('tasks/', TaskListAPIView.as_view(), name="task-list"),
    path('tasks/<int:pk>/', views.getTask, name="task-detail"),

    path('marks/', MarkListAPIView.as_view(), name="mark-list"),
    path('marks/<int:pk>/', views.getMark, name="mark-detail"),

    path('stories/', UserStoriesApiView.as_view(), name="stories"),
    path('stories/<int:story_id>/', UserStoriesUpdateAndDetailsApiView.as_view(), name="stories-id"),

]
