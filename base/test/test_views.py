import email
from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser, User

from base.models import Room



class ApiTestCases(TestCase):
    def setUp(self) -> None:
        self.user = User(
            email = "te@te.com",
            username = "test"
        )
        self.user.set_password("test1234")
        self.user.save()

        return super().setUp()

    def est_add_rooms_and_details(self):
        payload = {
            "name": "test room 2",
            "description": "somethign",
            "host": self.user.pk
        }
        response = self.client.post(reverse('room-list'), data=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], payload["name"])
        self.assertEqual(response.data["host"],self.user.pk )
        self.assertEqual(response.data["description"], payload["description"])

        # Testing task list 
        response = self.client.get(reverse('room-list'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_tasks(self):
        # Create a room for testing tasks
        room = Room.objects.create(
            host=self.user,
            name = "test room",
            description = "tt"
        )

        # Task to be created
        payload = {
            "body": "some test task",
            "room": room.pk
        }
        response = self.client.post(reverse('task-list'), data=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["body"], payload["body"])
        self.assertEqual(response.data["room"], room.pk )

        # Testing get task list 
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

