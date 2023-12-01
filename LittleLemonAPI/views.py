from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Cart, Category, Order, OrderItem
from .serializers import ( 
  UserSerializer, 
  DeleteUserSerializer, 
  MenuItemSerializer, 
  CartSerializer, 
  CategorySerializer, 
  OrderItemSerializer, 
  OrderSerializer
)
from .permissions import IsDeliveryCrew, IsManager

# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
  queryset = MenuItem.objects.all()
  serializer_class = MenuItemSerializer
  
  def get_permissions(self):
    permission_class = []
    if self.request.method != 'GET':
      permission_class = [IsManager]
    else:
      permission_class = [IsAuthenticated]
    return [permission() for permission in permission_class]
  
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
  queryset = MenuItem.objects.all()
  serializer_class = MenuItemSerializer
  
  def get_permissions(self):
    permission_class = []
    if self.request.method == 'GET':
      permission_class = [IsAuthenticated]
    else:
      permission_class = [IsManager]
    return [permission() for permission in permission_class]
  
class ManagerGroupView(generics.ListCreateAPIView):
  queryset = User.objects.filter(groups__name='Managers')
  permission_classes = [IsManager]
  serializer_class = UserSerializer

class ManagerView(generics.DestroyAPIView):
  queryset = User.objects.filter(groups__name='Managers')
  serializer_class = DeleteUserSerializer

class DeliveryCrewView(generics.ListCreateAPIView):
  queryset = User.objects.filter(groups__name='Delivery crew')
  permission_classes = [IsManager]
  serializer_class = UserSerializer

class DeleteDeliveryCrewMemberView(generics.DestroyAPIView):
  queryset = User.objects.filter(groups__name='Managers')
  serializer_class = DeleteUserSerializer
  
class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
  serializer_class = CartSerializer
  permission_classes = [IsAuthenticated]
  
  def get_queryset(self):
    cart = Cart.objects.filter(user=self.request.user)
    return cart
  
class OrderView(generics.ListCreateAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = OrderSerializer
  
  def perform_create(self, serializer):
    cart_items = self.get_cart_items()
    total = self.calculate_total(cart_items)
    order = self.create_order(serializer, total)
    
    self.create_order_items(cart_items, order)
    self.delete_cart_items(cart_items)
    
  def get_cart_items(self):
    return Cart.objects.filter(user=self.request.user)
  
  def create_order(self, serializer, total):
    return serializer.save(user=self.request.user, total=total)
  
  def create_order_items(self, cart_items, order):
    order_items = [
      OrderItem(
        menuitem=item.menuitem,
        quantity=item.quantity,
        unit_price=item.unit_price,
        price=item.price,
        order=order
      )
      for item in cart_items
    ]
    OrderItem.objects.bulk_create(order_items)
  
  def delete_cart_items(self, cart_items):
    cart_items.delete()

  def calculate_total(self, cart_items):
    total = sum(item.price for item in cart_items)
    return total
      
  def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='manager').exists():
      return Order.objects.all()
    elif user.groups.filter(name='Delivery crew').exists():
      return Order.objects.filter(delivery_crew=user)
    else:
      return Order.objects.filter(user=user)

class OrderItemView(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = OrderItemSerializer
  
  def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='Managers').exists():
      return Order.objects.all()
    return Order.objects.filter(user=user)
  
  def get_permissions(self):
    # if method is delete & permission is Manager
    # if method is patch & permission is Delivery crew
    # if method is put or patch & permission is Customer...
    # if method is get & permission is Customer
    return super().get_permissions()