
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


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    members = models.ManyToManyField(User, related_name='members', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = BaseModelManager()
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name


class Deck(models.Model):
    name = models.CharField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
        

class Task(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=False)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    

    def __str__(self):
        return self.body[:50]


class Mark(models.Model):
    mark = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)