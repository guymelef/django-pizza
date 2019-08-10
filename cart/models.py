from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CartItem(models.Model):
    ORDER_STATUS = [
        ('CART', 'In Cart'),
        ('PAID', 'Paid'),
        ('CONF', 'Confirmed'),
        ('DLVR', 'Delivered'),
        ('DONE', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    category = models.CharField(max_length=200)
    menu_id = models.IntegerField()
    name = models.CharField(max_length=200)    
    size = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    addons = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=4,
        choices=ORDER_STATUS,
        default='CART',
    )
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by: {self.user} -- {self.quantity}x {self.name} [${self.sub_total}]"

class CheckoutItem(models.Model):
    ORDER_STATUS = [
        ('PAID', 'Paid'),
        ('CONF', 'Confirmed'),
        ('DLVR', 'Delivered'),
        ('DONE', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkout_time = models.DateTimeField(auto_now_add=True)
    cart_items = models.ManyToManyField(CartItem)
    grand_total = models.DecimalField(max_digits = 10, decimal_places=2)
    status = status = models.CharField(
        max_length=4,
        choices=ORDER_STATUS,
        default='PAID',
    )