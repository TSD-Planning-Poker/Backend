from django.contrib import admin
from .models import Deck, Room, Task, Mark, Invitation, UserStory


admin.site.register(Room)
admin.site.register(Deck)
admin.site.register(Task)
admin.site.register(Mark)
admin.site.register(Invitation)
admin.site.register(UserStory)