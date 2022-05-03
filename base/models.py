
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MaxValueValidator, MinValueValidator

# class User(AbstractUser):
#     username = models.CharField(max_length=200, unique=True)
#     email = models.EmailField(unique=True, null=True, blank=True)


class BaseModelManager(models.Manager):

    def tasks(self):
        tasks = Task.objects.filter(room = self)
        return tasks

class BaseModel(models.Model):

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Room(BaseModel):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    members = models.ManyToManyField(User, related_name='members', blank=True)
    closed = models.BooleanField(default=False)
    
    objects = BaseModelManager()

    def __str__(self):
        return self.name

class Invitation(BaseModel):
    from_user = models.ForeignKey(to=User, null=False, on_delete=models.DO_NOTHING, related_name='from_user_id')
    to_user = models.ForeignKey(to=User, null=False, on_delete=models.DO_NOTHING, related_name='to_user')
    room = models.ForeignKey(to=Room, null=False,  on_delete=models.DO_NOTHING)
    code = models.CharField( unique=True, max_length=300, null=False)
    accepted = models.BooleanField(default=False, null=False)

    def __str__(self):
        return self.code

class Deck(BaseModel):
    name = models.CharField(max_length=200)
    # room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    # creator = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, null=False)

    def __str__(self):
        return self.name

class UserStory(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200, null=False,)
    description = models.CharField(max_length=500, null=False,)
    created_by = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.title

class Task(BaseModel):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    user_story = models.ForeignKey(to=UserStory, on_delete=models.DO_NOTHING, null=True)
    created_by = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, null=False)
    
    def __str__(self):
        return self.body[:50]
class Mark(BaseModel):
    mark = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    evaluator = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, null=False)

    def __str__(self):
        return str(self.mark)