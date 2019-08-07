from django.contrib import admin

from .models import *

class SubInline(admin.StackedInline):
    model = Sub.add_Ons.through
    extra = 1

class SubExtraAdmin(admin.ModelAdmin):
    inlines = [SubInline]

class SubAdmin(admin.ModelAdmin):
    filter_horizontal = ("add_Ons",)

admin.site.register(PizzaType)
admin.site.register(RegularPizza)
admin.site.register(SicilianPizza)
admin.site.register(PizzaTopping)
admin.site.register(Sub, SubAdmin)
admin.site.register(SubExtra, SubExtraAdmin)
admin.site.register(Pasta)
admin.site.register(Salad)
admin.site.register(DinnerPlatter)