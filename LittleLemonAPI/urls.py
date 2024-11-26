from django.urls import path, include
from .views import *

urlpatterns = [
    path('menu-items', MenuItemList.as_view(), name="menuitem"),
    path('menu-items/<int:pk>', MenuItemDetail.as_view(), name="menuitem-detail"),
    path('categories', CategoryList.as_view(), name="category"),
    path('categories/<int:pk>', CategoryDetail.as_view(), name="category-detail"),
    path('cart/menu-items', CartItemList.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'}), name="cartitem"),
    path('cart/menu-items/<int:pk>', CartItemDetail.as_view(), name="cartitem-detail"),
    path('orders/', OrderList.as_view(), name="order"),
    path('orders/<int:pk>', OrderDetail.as_view(), name="order-detail"),
    path('groups/manager/users', ManagerUserList.as_view({'get': 'list', 'post': 'create'}), name="manager"),
    path('groups/manager/users/<int:pk>', RemoveManager.as_view(), name="remove-manager"),
    path('groups/delivery-crew/users', DeliveryCrewList.as_view({'get': 'list', 'post': 'create'}), name="delivery-crew"),
    path('groups/delivery-crew/users/<int:pk>', RemoveDeliveryCrew.as_view(), name="remove-delivery-crew"),
    path('users/all', UserList.as_view(), name="user"),
    path('', include('djoser.urls')),
]
