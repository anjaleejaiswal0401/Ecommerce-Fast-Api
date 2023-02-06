from tortoise.models import Model
from tortoise import Tortoise, fields
from fastapi import FastAPI
from tortoise import Tortoise


STATE_CHOICES = (
('Andaman & Nicobar Islands', 'Andaman & Nicobar Islands'),
('Andra Pradesh', 'Andra Pradesh'),
('Arunachal Pradesh', 'Arunachal Pradesh'),
('Assam', 'Assam'),
('Bihar', 'Bihar'),
('Chhattisgarh', 'Chhattisgarh'),
('chandigarh', 'chandigarh'),
('dadra & Nagar Haveli', 'dadra & Nagar Haveli'),
('Delhi', 'Delhi'),
('Madhya Pradesh', 'Madhya Pradesh'),
('Utter Pradesh', 'Utter Pradesh'),
('Andra Pradesh', 'Andra Pradesh'),
('Mumbai', 'Mumbai'),
('Mizoram', 'Mizoram'),
('Nagaland', 'Nagaland')
)

class State(Model):
    STATE_CHOICES = fields.CharField(choices=STATE_CHOICES, max_length=50)

class Create_user(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(50,)
    email = fields.CharField(50, unique=True)
    phone = fields.CharField(10)
    password = fields.CharField(200)


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(200, unique=True)
    slug = fields.CharField(30)
    is_active = fields.BooleanField(default=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class SubCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(200, unique=True)
    slug = fields.CharField(30)
    category = fields.ForeignKeyField("models.Category", related_name="subcategory", on_delete="CASCADE")
    is_active = fields.BooleanField(default=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class Photo(Model):
    product_image =fields.TextField()



class Add_products(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    price = fields.FloatField()
    slug = fields.CharField(30)
    discountprice= fields.CharField(100)
    category = fields.ForeignKeyField("models.Category", related_name="subcat", on_delete="CASCADE")
    description = fields.TextField()
    subcategory = fields.ForeignKeyField("models.SubCategory", related_name="products", on_delete="CASCADE")
    product_image = fields.TextField()
    is_active = fields.BooleanField(default=True)



class Addtocart(Model):
    id =fields.IntField(pk=True)
    user= fields.ForeignKeyField("models.Create_user", related_name= "cartadd", on_delete="CASCADE")     
    product_d = fields.ForeignKeyField("models.Add_products", related_name= "cartad", on_delete="CASCADE")     
    

class Order(Model):
    id =fields.IntField(pk=True)
    orderuser= fields.ForeignKeyField("models.Create_user", related_name= "cartor", on_delete="CASCADE")
    subtotal = fields.FloatField() 
    shipping = fields.FloatField()
    total = fields.FloatField()

class Billing(Model):
    id = fields.IntField(pk=True)
    orderuser= fields.ForeignKeyField("models.Create_user", related_name= "bil", on_delete="CASCADE")
    name = fields.CharField(50,)
    email = fields.CharField(50, unique=True)
    phone = fields.CharField(10)
    address = fields.CharField(50,)
    city = fields.CharField(50,)
    state = fields.CharField(choices=STATE_CHOICES,max_length=200)
    pincode = fields.CharField(10)
    billingorder= fields.ForeignKeyField("models.Order", related_name= "bill", on_delete="CASCADE")

class Orderhistory(Model):
    id =fields.IntField(pk=True)
    orderuser= fields.ForeignKeyField("models.Create_user", related_name= "confirm", on_delete="CASCADE")
    ordernumber =fields.CharField(50)
    name = fields.CharField(50,)
    email = fields.CharField(50, unique=True)
    phone = fields.CharField(10)
    address = fields.CharField(50,)
    city = fields.CharField(50,)
    state = fields.CharField(50)
    pincode = fields.CharField(10)
    subtotal = fields.FloatField() 
    shipping = fields.FloatField()
    total = fields.FloatField()
    
    

    

    

    Tortoise.init_models(['ecom_API.models'], 'models')
