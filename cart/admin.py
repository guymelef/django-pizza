from django.contrib import admin

from .models import CartItem, CheckoutItem

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'name', 'added_on', 'status')
    readonly_fields = ('added_on',)
    fieldsets = [
        ('Customer', {'fields': ['user']}),
        ('Menu Item', {'fields': ['added_on', 'category', 'menu_id', 'price', 'size', 'addons']}),
        ('Order Status', {'fields': ['status', 'sub_total']}),
    ]
    list_filter = ['status', 'user', 'added_on']

class CheckoutItemAdmin(admin.ModelAdmin):
    readonly_fields = ('checkout_time',)
    list_display = ('user', 'checkout_time', 'grand_total', 'status')
    list_filter = ['user', 'checkout_time']
    filter_horizontal = ('cart_items',)

admin.site.register(CartItem, CartItemAdmin)
admin.site.register(CheckoutItem, CheckoutItemAdmin)