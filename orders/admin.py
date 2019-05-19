from django.contrib import admin

from .models import RegularPizza, SicilianPizza, PizzaTopping, SubExtra, Sub, Pasta, Salad, DinnerPlatter

# Register your models here.
admin.site.register(RegularPizza)
admin.site.register(SicilianPizza)
admin.site.register(PizzaTopping)
admin.site.register(SubExtra)
admin.site.register(Sub)
admin.site.register(Pasta)
admin.site.register(Salad)
admin.site.register(DinnerPlatter)