from django.db import models


class Warehouse(models.Model):
    id = models.IntegerField(primary_key=True)
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        db_table = 'warehouse'


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField()

    class Meta:
        db_table = 'product'


class Inventory(models.Model):
    id = models.IntegerField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    remain_count = models.IntegerField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    class Meta:
        db_table = 'inventory'


class Order(models.Model):
    package_id = models.IntegerField(primary_key=True)
    status = models.TextField() # Delivered, OutForDelivery, Packed, Processing
    truck_id = models.IntegerField(null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    addr_x = models.IntegerField()
    addr_y = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    time = models.DateTimeField(default=None, null=True)

    class Meta:
        db_table = 'order'

