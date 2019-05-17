from django.db import models

# Create your models here.
class PizzaTopping(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Pasta(models.Model):
    name = models.CharField(max_length=64)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} - ${self.price}"

class Salad(models.Model):
    name = models.CharField(max_length=64)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} - ${self.price}"

class DinnerPlatter(models.Model):
    name = models.CharField(max_length=64)
    small_price = models.IntegerField()
    large_price = models.IntegerField()