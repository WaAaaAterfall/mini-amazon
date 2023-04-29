from django.contrib import admin


from .models import *
# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Warehouse)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(AmazonUser)
admin.site.register(Category)

