from django.urls import path
from . import views

urlpatterns = [
  path('menu-items/', ),
  path('menu-items/<int:pk>/', ),
  path('groups/manager/users/', ),
  path('groups/manager/users/<int:pk>/', ),
  path('groups/delivery-crew/users/', ),
  path('groups/delivery-crew/users/<int:pk>/', ),
  path('cart/menu-items', ),
  path('orders/', ),
  path('orders/<int:pk>/', ),
]