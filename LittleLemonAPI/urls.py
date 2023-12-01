from django.urls import path
from . import views

urlpatterns = [
  path('menu-items/', views.MenuItemsView.as_view()),
  path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
  path('groups/manager/users/', views.ManagerGroupView.as_view()),
  path('groups/manager/users/<int:pk>/', views.ManagerView.as_view()),
  path('groups/delivery-crew/users/', views.DeliveryCrewView.as_view()),
  path('groups/delivery-crew/users/<int:pk>/', views.DeleteDeliveryCrewMemberView.as_view()),
  path('cart/menu-items', views.CartView.as_view()),
  path('orders/', views.OrderView.as_view()),
  # path('orders/<int:pk>/', ),
]