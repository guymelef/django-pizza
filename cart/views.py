from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import CartItem
from orders.models import RegularPizza, SicilianPizza, PizzaTopping, Sub, SubExtra, Pasta, Salad, DinnerPlatter


# Create your views here.
@login_required
def cart(request):
    user = request.user.id
    cart_items = CartItem.objects.filter(user=user, status='CART')
    context = {
        'cart_items': cart_items
    }

    return render(request, 'cart/cart.html', context)

@login_required
def checkout(request):
    return HttpResponse('Check out orders here.')

@login_required
def addorder(request):
    if request.is_ajax():
        user = User.objects.get(pk=request.user.id)
        cart_item = CartItem()
        data = {
            'category': request.POST.get('category', None),
            'type': request.POST.get('type', None),
            'size': request.POST.get('size', None),
            'quantity': request.POST.get('quantity', None),
            'toppings': request.POST.getlist('toppings[]', None),
            'extras': request.POST.getlist('extras[]', None),         
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
            pizzaSize = sizeType[0].title()
            pizzaID = int(sizeType[1])

            if data['type'] == 'RegularPizza':
                try:
                    pizza = RegularPizza.objects.get(pk=pizzaID)
                    pizzaName = f'Regular Pizza ({pizza.name})'
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            elif data['type'] == 'SicilianPizza':
                try:
                    pizza = SicilianPizza.objects.get(pk=pizzaID)
                    pizzaName = f'Sicilian Pizza ({pizza.name})'
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            else:
                return JsonResponse({'error': 'Please fix your order!'})

            if pizzaSize == 'Small':
                price = float(pizza.small)
            elif pizzaSize == 'Large':
                price = float(pizza.large)
            else:
                return JsonResponse({'error': 'Please fix your order!'})

            new_order = {'quantity': quantity, 'category': data['type'], 'menu_id': pizzaID, 'name': pizzaName, 'size': pizzaSize, 'price': format(price, '.2f')}
            sub_total = price * quantity
            new_order['sub_total'] = format(sub_total, '.2f')
            
            if len(data['toppings']) > 0 and len(data['toppings']) == pizza.toppingsCount:
                addons = []
                for topping in data['toppings']:
                    try:
                        topping = PizzaTopping.objects.get(pk=topping)
                        if topping.name in addons:
                            return JsonResponse({'error': 'Please fix your order!'})
                        addons.append(topping.name)
                    except:
                        return JsonResponse({'error': 'Please fix your order!'})
                addons = ', '.join(addons)
                new_order['addons'] = addons
            elif len(data['toppings']) != pizza.toppingsCount:
                return JsonResponse({'error': 'Please fix your order!'})       

        # Validate sub order
        elif (data['category'] == 'sub'):
            subSize = data['size'].title()
            subType = int(data['type'])

            try:
                sub = Sub.objects.get(pk=subType)
            except:
                return JsonResponse({'error': 'Please fix your order!'})
            
            if subSize == 'Small':
                price = float(sub.small)
            elif subSize == 'Large':
                price = float(sub.large)
            else:
                return JsonResponse({'error': 'Please fix your order!'})

            new_order = {'category': 'Sub', 'name': sub.name + " Sub", 'menu_id': subType, 'size': subSize, 'quantity': quantity, 'price': format(price, '.2f')}
            
            addonsTotal = 0
            if len(data['extras']) > 0:
                addons = []
                for extra in data['extras']:
                    try:
                        extra = SubExtra.objects.get(pk=extra)
                        if extra.name in addons:
                            return JsonResponse({'error': 'Please fix your order!'})
                        addons.append(extra.name)
                        addonsTotal += float(extra.price)
                    except:
                        return JsonResponse({'error': 'Please fix your order!'})
                addons = ', '.join(addons)
                new_order['addons'] = addons

            sub_total = (price * quantity) + (addonsTotal * quantity)
            new_order['sub_total'] = format(sub_total, '.2f')

        # Validate dinner platter order
        elif (data['category'] == 'dinnerPlatter'):
            dinnerPlatterSize = data['size'].title()
            dinnerPlatterType = int(data['type'])
            try:
                dinnerPlatter = DinnerPlatter.objects.get(pk=dinnerPlatterType)
            except:
                return JsonResponse({'error': 'Please fix your order!'})

            if dinnerPlatterSize == 'Small':
                price = float(dinnerPlatter.small)
            elif dinnerPlatterSize == 'Large':
                price = float(dinnerPlatter.large)
            else:
                return JsonResponse({'error': 'Please fix your order!'})
            
            new_order = {'category': 'DinnerPlatter', 'name': dinnerPlatter.name + " Dinner Platter", 'menu_id': dinnerPlatterType, 'size': dinnerPlatterSize, 'quantity': quantity, 'price': format(price, '.2f')}
            new_order['sub_total'] = format(quantity * price, '.2f')
                    
        # validata pasta/salad order
        elif data['category'] in ['pasta', 'salad']:
            category = data['category'].title()
            menuType = int(data['type'])

            if category == 'Pasta':
                try:
                    menuItem = Pasta.objects.get(pk=menuType)
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            if category == 'Salad':
                try:
                    menuItem = Salad.objects.get(pk=menuType)
                except:
                    return JsonResponse({'error': 'Please fix your order!'})
            
            new_order = {'category': category, 'name': menuItem.name, 'menu_id': menuType, 'quantity': quantity, 'price': format(menuItem.price, '.2f')}
            new_order['sub_total'] = format(quantity * menuItem.price, '.2f')

        # if category is not valid
        else:
            return JsonResponse({'error': 'Please fix your order!'})

        # Save order to db
        cart_item.user = user
        cart_item.quantity = new_order['quantity']
        cart_item.category = new_order['category']
        cart_item.menu_id = new_order['menu_id']
        cart_item.name = new_order['name']
        if 'size' in new_order:
            cart_item.size = new_order['size']
        if 'addons' in new_order:
            cart_item.addons = new_order['addons']
        cart_item.price = float(new_order['price'])
        cart_item.sub_total = float(new_order['sub_total'])
        cart_item.save()

        cart_total = 0
        cart_items = CartItem.objects.filter(
            user = user,
            status = 'CART',
        )
        for item in cart_items:
            cart_total += item.sub_total
        new_order['cart_total'] = format(cart_total, '.2f')
        new_order['order_id'] = cart_item.id

        print(new_order)
        return JsonResponse(new_order)
    
    # if user reaches page by other request method 
    else:
        raise Http404

@login_required
def deleteorder(request):
    if request.is_ajax():
        user = User.objects.get(pk=request.user.id)
        order_id = request.POST.get('order_id')
        print(order_id)
        try:
            item = CartItem.objects.get(pk=order_id, user=user)
            item.delete()
        except:
            return JsonResponse({'error': 'Please fix your order!'})
        
        cart_items = CartItem.objects.filter(user=user, status='CART')
        cart_total = 0
        for item in cart_items:
            cart_total += item.sub_total
        cart_total = format(cart_total, '.2f')

        return JsonResponse({'success': True, 'cart_total': cart_total})

    # if user reaches page by other request method 
    else:
        raise Http404