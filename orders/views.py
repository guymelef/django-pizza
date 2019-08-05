from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from .models import *


# Create your views here.
def home(request):
    # Prepare cart
    if request.session.get('cart_items') is None:
            request.session['cart_items'] = []
    
    # set up all menu items
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
        "cart_items" : request.session['cart_items'],
    }

    cart_total = 0
    for item in request.session['cart_items']:
        cart_total += float(item['total'])
    if cart_total != 0:
        context['cart_total'] = format(cart_total, '.2f')

    return render(request, "orders/home.html", context)

@login_required
def addorder(request):
    if request.is_ajax():

        # Store orders to session before saving to db
        order_id = request.session.get('order_id', 0)

        data = {
            'category': request.GET.get('category', None),
            'type': request.GET.get('type', None),
            'size': request.GET.get('size', None),
            'quantity': request.GET.get('quantity', None),
            'toppings': request.GET.getlist('toppings[]', None),
            'extras': request.GET.getlist('extras[]', None),          
            }

        # Validate quantity
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                return JsonResponse({'error': 'Please fix your order!'})
        except:
            return JsonResponse({'error': 'Please fix your order!'})

        # Validate each detail of the order
        if data['category'] == 'pizza':
            sizeType = data['size'].split('-')
            pizzaSize = sizeType[0]
            pizzaType = sizeType[1]
            if data['type'] == 'regularPizza':
                variant = 'Regular Pizza'
                try:
                    pizza = RegularPizza.objects.get(pk=pizzaType)
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            elif data['type'] == 'sicilianPizza':
                variant = 'Sicilian Pizza'
                try:
                    pizza = SicilianPizza.objects.get(pk=pizzaType)
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            else:
                return JsonResponse({'error': 'Please fix your order!'})

            if pizzaSize == 'small':
                price = float(pizza.small)
            elif pizzaSize == 'large':
                price = float(pizza.large)
            else:
                return JsonResponse({'error': 'Please fix your order!'})

            newOrder = {'category': 'Pizza', 'type': variant, 'name': variant + f' ({pizza.name})', 'id': pizzaType, 'size': pizzaSize.title(), 'quantity': quantity, 'price': format(price, '.2f')}
            
            toppings = []
            addons = []
            if len(data['toppings']) > 0 and len(data['toppings']) == pizza.toppingsCount:
                for topping in data['toppings']:
                    try:
                        topping = PizzaTopping.objects.get(pk=topping)
                        toppings.append(topping.name)
                        addons.append(topping.id)
                    except:
                        return JsonResponse({'error': 'Please fix your order!'})
                toppingsStr = ', '.join(toppings)
                newOrder['extras'] = toppingsStr
                newOrder['addons'] = addons
            elif len(data['toppings']) != pizza.toppingsCount:
                return JsonResponse({'error': 'Please fix your order!'})        

            total = float(newOrder['price']) * newOrder['quantity']
            newOrder['total'] = format(float(total), '.2f')
            newOrder['order_id'] = order_id

            request.session['cart_items'].append(newOrder)
            request.session['order_id'] = order_id + 1  
                    
        # Validate sub order
        elif (data['category'] == 'sub'):
            subSize = data['size']
            subType = data['type']
            try:
                sub = Sub.objects.get(pk=subType)
            except:
                return JsonResponse({'error': 'Please fix your order!'})
            
            if subSize == 'small':
                price = float(sub.small)
            elif subSize == 'large':
                price = float(sub.large)
            else:
                return JsonResponse({'error': 'Please fix your order!'})

            newOrder = {'category': 'Sub', 'name': sub.name + " Sub", 'id': subType, 'size': subSize.title(), 'quantity': quantity, 'price': format(price, '.2f')}

            extras = []
            addons = []
            extrasTotal = 0
            if len(data['extras']) > 0:
                for extra in data['extras']:
                    try:
                        extra = SubExtra.objects.get(pk=extra)
                        extras.append(extra.name)
                        addons.append(extra.id)
                        extrasTotal += float(extra.price)
                    except:
                        return JsonResponse({'error': 'Please fix your order!'})
                extrasStr = ', '.join(extras)
                newOrder['extras'] = extrasStr
                newOrder['addons'] = addons

            total = float(newOrder['price']) * newOrder['quantity'] + (extrasTotal * newOrder['quantity'])
            newOrder['total'] = format(float(total), '.2f')
            newOrder['order_id'] = order_id

            request.session['cart_items'].append(newOrder)
            request.session['order_id'] = order_id + 1

        # Validate dinner platter order
        elif (data['category'] == 'dinnerPlatter'):
            dinnerPlatterSize = data['size']
            dinnerPlatterType = data['type']
            try:
                dinnerPlatter = DinnerPlatter.objects.get(pk=dinnerPlatterType)
            except:
                return JsonResponse({'error': 'Please fix your order!'})

            if dinnerPlatterSize == 'small':
                price = float(dinnerPlatter.small)
            elif dinnerPlatterSize == 'large':
                price = float(dinnerPlatter.large)
            else:
                return JsonResponse({'error': 'Please fix your order!'})
            
            newOrder = {'category': 'Dinner Platter', 'name': dinnerPlatter.name + " Dinner Platter", 'id': dinnerPlatterType, 'size': dinnerPlatterSize.title(), 'quantity': quantity, 'price': format(price, '.2f')}
            newOrder['total'] = format(newOrder['quantity'] * float(newOrder['price']), '.2f')
            newOrder['order_id'] = order_id

            request.session['cart_items'].append(newOrder)
            request.session['order_id'] = order_id + 1
                    
        # validata pasta/salad order
        elif data['category'] in ['pasta', 'salad']:
            category = data['category']
            menuType = data['type']
            menuItem =""
            if category == 'pasta':
                try:
                    menuItem = Pasta.objects.get(pk=menuType)
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            if category == 'salad':
                try:
                    menuItem = Salad.objects.get(pk=menuType)
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            
            newOrder = {'category': category.title(), 'name': menuItem.name, 'id': menuType, 'quantity': quantity, 'price': format(menuItem.price, '.2f')}
            newOrder['total'] = format((newOrder['quantity'] * float(newOrder['price'])), '.2f')
            newOrder['order_id'] = order_id

            request.session['cart_items'].append(newOrder)             
            request.session['order_id'] = order_id + 1
        
        # if category is not valid
        else:
            return JsonResponse({'error': 'Please fix your order!'})

        cart_total = 0
        for item in request.session['cart_items']:
            cart_total += float(item['total'])
        cart_total = format(cart_total, '.2f')
        newOrder['cart_total'] = cart_total

        print(newOrder)
        return JsonResponse(newOrder)
    else:
        raise Http404

@login_required
def deleteorder(request):
    if request.is_ajax():
        order_id = int(request.POST.get('order_id'))
        cart_items = request.session['cart_items']

        itemIndex = None
        for item in cart_items:
            if item['order_id'] == order_id:
                itemIndex = cart_items.index(item)

        if itemIndex == None:
            return JsonResponse({'error': True})
        else:
            del request.session['cart_items'][itemIndex]
            cart_total = 0
            for item in request.session['cart_items']:
                cart_total += float(item['total'])
            cart_total = format(cart_total, '.2f')
            return JsonResponse({'success': True, 'cart_total': cart_total})
    else:
        raise Http404