from django.db import models

# Create your models here.
class PizzaType(models.Model):
    alias = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=120)
    
    def __str__(self):
        return f"{self.name} - {self.description}"

class RegularPizza(models.Model):
    name = models.CharField(max_length=120, unique=True)
    small = models.DecimalField(max_digits=10, decimal_places=2)
    large = models.DecimalField(max_digits=10, decimal_places=2)
    toppingsCount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - Small (${self.small}) | Large (${self.large})"

class SicilianPizza(models.Model):
    name = models.CharField(max_length=120, unique=True)
    small = models.DecimalField(max_digits=10, decimal_places=2)
    large = models.DecimalField(max_digits=10, decimal_places=2)
    toppingsCount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - Small (${self.small}) | Large (${self.large})"

class PizzaTopping(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return f"{self.name}"
        
class SubExtra(models.Model):
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class Sub(models.Model):
    name = models.CharField(max_length=120, unique=True)
    small = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    large = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    add_Ons = models.ManyToManyField(SubExtra, blank=True, related_name="extras")

    def __str__(self):
        return f"{self.name} - Small (${self.small}) | Large (${self.large})"

class Pasta(models.Model):
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class Salad(models.Model):
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class DinnerPlatter(models.Model):
    name = models.CharField(max_length=120, unique=True)
    small = models.DecimalField(max_digits=10, decimal_places=2)
    large = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - Small (${self.small}) | Large (${self.large})"