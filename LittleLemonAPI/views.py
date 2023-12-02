from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import ( 
  UserSerializer, 
  DeleteUserSerializer, 
  MenuItemSerializer, 
  CartSerializer, 
  OrderItemSerializer, 
  OrderSerializer,
)
from .permissions import IsDeliveryCrew, IsManager

# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
  queryset = MenuItem.objects.all()
  serializer_class = MenuItemSerializer
  throttle_classes = [UserRateThrottle]
  pagination_class = PageNumberPagination
  pagination_class.page_size = 5
  search_fields = ['title']
  ordering_fields = ['price']
  
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
  throttle_classes = [UserRateThrottle]
  
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
  throttle_classes = [UserRateThrottle]
  
  def get_queryset(self):
    cart = Cart.objects.filter(user=self.request.user)
    return cart
  
class OrderView(generics.ListCreateAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = OrderSerializer
  throttle_classes = [UserRateThrottle]
  search_fields = ['menu_item']
  
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
      ) for item in cart_items
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
  permission_classes = [IsAuthenticated]
  
  def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='Managers').exists():
      return OrderItem.objects.filter(id=self.kwargs['pk'])
    else:
      return OrderItem.objects.filter(order__user=user, id=self.kwargs['pk'])
  
  def get_permissions(self):
    # if method is delete & permission is Manager
    # if method is patch & permission is Delivery crew
    # if method is put or patch & permission is Customer...
    # if method is get & permission is Customer
    if self.request.method == 'DELETE':
      return [IsManager()]
    return super().get_permissions()
  
  def partial_update(self, request, *args, **kwargs):
    instance = self.get_object()
    user = self.request.user
    
    if user.groups.filter(name='Delivery crew').exists():
      if 'status' in request.data.keys():
        instance.status = request.data['status']
        instance.save(update_fields=['status'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
      
    if user.groups.filter(name='Managers').exists():
      if 'status' in request.data.keys():
        instance.status = request.data['status']
      if 'delivery_crew' in request.data.keys():
        instance.delivery_crew = request.data['delivery_crew']
        
      instance.save(update_fields=['status','delivery_crew'])
      serializer = self.get_serializer(instance)
      return Response(serializer.data)
    
    return Response(
      {"message": "You are not authorized to perform this action."},
      status=status.HTTP_403_FORBIDDEN
    )