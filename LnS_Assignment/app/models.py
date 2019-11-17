from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_slug, validate_email
# Create your models here.

class Contact(models.Model):

    name = models.CharField(max_length=100, null=False)
    phone = models.CharField(max_length=100, null=False)
    email = models.EmailField(validators=[validate_email], max_length=100, null=True)
    spam = models.BooleanField(default=False)

    def __str__(self):

        return self.name

class UserContactMapping(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=False)
    def __str__(self):

        return str(self.user) + ',' + str(self.contact)

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    phone = models.CharField(max_length=15, null=False, unique=True)
    spam = models.BooleanField(default=False)

    def __str__(self):

        return str(self.user)
        
