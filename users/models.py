from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    user_cred_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = PhoneNumberField()
    age = models.IntegerField(default=18)
    gender = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='users/images', default='')

    def __str__(self):
        return self.name

class Request(models.Model):
    id = models.AutoField(primary_key=True)
    request_create_date = models.DateField()
    trip_date_time = models.DateTimeField()
    desc = models.CharField(max_length=100)
    no_passengers = models.IntegerField()
    request_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_users = models.ManyToManyField(
        User, related_name='request_received')


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages')
    request_id = models.ForeignKey(Request, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    message_date = models.DateField()


class Requested_users_status(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_user', default=1)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
