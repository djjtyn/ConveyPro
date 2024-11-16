from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length = 500)

    def __str__(self):
        return self.name

class UserType(models.Model):
    type = models.CharField(max_length = 100)

    def __str__(self):
        return self.type

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Ensure the user is a superuser and staff
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        # Return a user by email (since email is the natural key now)
        return self.get(email=email)

#Custom User model which extends AbstractUser class to allow additional attributes
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    company = models.ForeignKey('Company', on_delete = models.SET_NULL, null = True)
    user_type = models.ForeignKey('UserType', on_delete = models.SET_NULL, null = True)
    is_verified = models.BooleanField() 
    # This wil lbe used to store user entered company values prior to creating them in the Company table
    non_verified_company = models.CharField(max_length = 400)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email