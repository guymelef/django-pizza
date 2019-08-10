import os
from django.conf import settings

from django.shortcuts import render
from django.http import JsonResponse

from .models import PizzaType, RegularPizza, SicilianPizza, PizzaTopping, Sub, SubExtra, Pasta, Salad, DinnerPlatter
from cart.models import CartItem


# Create your views here.
def home(request):

    if request.is_ajax():
        if request.POST['data'] == 'hbtext':
            modal = open(os.path.join(settings.BASE_DIR, 'modalForm.txt'))
            cart = open(os.path.join(settings.BASE_DIR, 'cartItem.txt'))
            modal_form = modal.read()
            cart_text = cart.read()
            modal.close()
            cart.close()

            return JsonResponse({'modal_form' : modal_form, 'cart_text' : cart_text})
    else:
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
        }

        if request.user.is_authenticated:
            user = request.user.id
            cart_items = CartItem.objects.filter(user=user, status='CART')
            context['cart_items'] = cart_items
            cart_total = 0
            cart_quantity = 0
            for item in cart_items:
                cart_total += item.sub_total
                cart_quantity += item.quantity
            if cart_total != 0:
                context['cart_total'] = format(cart_total, '.2f')
            context['cart_quantity'] = cart_quantity

        return render(request, "orders/home.html", context)