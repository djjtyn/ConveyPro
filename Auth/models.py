from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length = 500)

    def __str__(self):
        return self.name

class UserType(models.Model):
    type = models.CharField(max_length = 100)

    def __str__(self):
        return self.type

#Custom User model which extends AbstractUser class to allow additional attributes
class CustomUser(AbstractUser):
    company = models.ForeignKey('Company', on_delete = models.SET_NULL, null = True)
    user_type = models.ForeignKey('UserType', on_delete = models.SET_NULL, null = True)

    def __str__(self):
        return self.username