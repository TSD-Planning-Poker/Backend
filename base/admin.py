from django.contrib import admin
from .models import Deck, Room, Task, User


# admin.site.register(User)
admin.site.register(Room)
admin.site.register(Deck)
admin.site.register(Task)