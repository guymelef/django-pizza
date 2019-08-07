from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from .models import PizzaType, RegularPizza, SicilianPizza, PizzaTopping, Sub, SubExtra, Pasta, Salad, DinnerPlatter
from cart.models import CartItem


# Create your views here.
def home(request):
    user = request.user.id
    cart_items = CartItem.objects.filter(user=user, status='CART')

    # Set up all menu items
    pizzaType = list(PizzaType.objects.values().order_by('name'))
    regularPizza = list(RegularPizza.objects.values().order_by('small'))
    sicilianPizza = list(SicilianPizza.objects.values().order_by('small'))
    pizzaTopping = list(PizzaTopping.objects.values().order_by('name'))
    subs = Sub.objects.all().order_by('name')
    pasta = list(Pasta.objects.values().order_by('name'))
    salad= list(Salad.objects.values().order_by('name'))
    dinnerPlatter = list(DinnerPlatter.objects.values().order_by('name'))
    context = {
        "pizzaType" : pizzaType,
        "regularPizza" : regularPizza,
        "sicilianPizza" : sicilianPizza,
        "pizzaTopping" : pizzaTopping,
        "subs" : subs,
        # for sub JSON
        "sub" : list(Sub.objects.values('id', 'name', 'small', 'large', 'add_Ons__id', 'add_Ons__name', 'add_Ons__price')),
        "pasta" : pasta,
        "salad" : salad,
        "dinnerPlatter" : dinnerPlatter,
        "cart_items" : cart_items,
    }

    cart_total = 0
    for item in cart_items:
        cart_total += item.sub_total
    if cart_total != 0:
        context['cart_total'] = format(cart_total, '.2f')

    return render(request, "orders/home.html", context)