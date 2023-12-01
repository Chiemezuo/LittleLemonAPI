from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, Cart, MenuItem, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id','username','email']
    
class DeleteUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id']

class MenuItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = MenuItem
    fields = ['id','title','price','category','featured']

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ['id','title','slug']

class CartSerializer(serializers.ModelSerializer):
  class Meta:
    model = Cart
    fields = ['id','user','menuitem','quantity','unit_price','price']

class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Order
    fields = ['id','user','delivery_crew','status','total','date']

class OrderItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderItem
    fields = ['id','order','menuitem','quantity','unit_price','price']