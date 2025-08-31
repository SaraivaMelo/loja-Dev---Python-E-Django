from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Address(models.Model):
    cep = models.CharField(max_length=9)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    neighborhood = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.number} - {self.neighborhood} ({self.city}/{self.state})"

    
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    points = models.IntegerField(default=0) 

    def __str__(self):
        return self.user.get_full_name() or self.user.username