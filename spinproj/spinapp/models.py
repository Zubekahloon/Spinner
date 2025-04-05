from django.db import models

class User(models.Model):
    name = models.CharField(max_length=150)
    territory  = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class AssignedHouse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house_number = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"House {self.house_number} -> {self.user.name}"


class House(models.Model):
    house_number = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.house_number
