from django.db import models
from django.contrib.auth.models import User

class AmazonUser(User):
    ups_account = models.TextField(blank=True)
    def __str__(self):
        return super().get_username()



class Warehouse(models.Model):
    id = models.IntegerField(primary_key=True)
    world_id = models.IntegerField(default=1)
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        db_table = 'warehouse'


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField(default='Apple Watch')
    description = models.TextField()
    price = models.FloatField(default=1 ,blank=False, null=False)
    img = models.CharField(max_length=50, default="/static/img/sample.jpg")
    sales = models.IntegerField(default=0)

    class Meta:
        db_table = 'product'
    def __str__(self):
        return f"{self.id} - {self.title}"


class Inventory(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    remain_count = models.IntegerField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    class Meta:
        db_table = 'inventory'


class Order(models.Model):
    package_id = models.AutoField(primary_key=True)
    count = models.IntegerField(default=0)
    status = models.TextField(default='Processing') # Delivered, OutForDelivery, Packed, Processing
    truck_id = models.IntegerField(null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse,  null=True, blank=True, on_delete=models.CASCADE)
    addr_x = models.IntegerField()
    addr_y = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE,default=1)
    user = models.ForeignKey(AmazonUser,on_delete=models.CASCADE,default=4)
    count = models.IntegerField(default=1)
    ups_account = models.TextField(default='ups_huidan',null=True, blank=True)

  
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    

    class Meta:
        db_table = 'order'
    


class Cart(models.Model):
    user = models.ForeignKey(AmazonUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

class Category(models.Model):
    name = models.TextField()
    Product = models.ForeignKey(Product,on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.Product.id}"
