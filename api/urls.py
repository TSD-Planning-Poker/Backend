from django.urls import path
from . import views
from .room_views import RoomInvitations, AcceptInviteApiView

urlpatterns = [
    path('rooms/', views.RoomListCreateAPIView.as_view(), name="room-list"),
    path('rooms/<int:id>/userstories/', views.get_userstories_from_room, name="room_userstories"),
    path('rooms/<int:id>/allusers/', views.get_users_from_room, name="room-alltasks"),
    path('rooms/<int:pk>/', views.RoomsUpdateAndDetailsView.as_view(), name="room-detail"),
    path('rooms/<int:pk>/leave/', views.leave_room, name="room-join"),

    path('tasks/', views.TaskListAPIView.as_view(), name="task-list"),
    path('tasks/<int:pk>/', views.TasksDetailsAndUpdateApiView.as_view(), name="task-detail"),

    path('marks/', views.MarkListAPIView.as_view(), name="mark-list"),
    path('marks/<int:pk>/', views.getMark, name="mark-detail"),
    path('marks/<int:pk>/update', views.updateMark, name="mark-detail"),

    path('stories/', views.UserStoriesApiView.as_view(), name="stories"),
    path('stories/<int:id>/tasks', views.get_tasks_in_story, name="stories_in_task"),
    path('stories/<int:id>/allmarks', views.get_marks_from_userstories, name="mark-listmark"),
    path('stories/<int:story_id>/', views.UserStoriesUpdateAndDetailsApiView.as_view(), name="stories-id"),

    path('invitations/', RoomInvitations.as_view(), name="invitations"),
    path('invitations/<str:invitation_code>/accept/', AcceptInviteApiView.as_view(), name="accept_invitations"),

    path('export/<str:delimeter>/', views.ExportCSV_withDelimeter.as_view(), name="export_with_delimeter"),

    path('change_password/<int:pk>/', views.ChangePassword.as_view(), name="change_password"),

]
