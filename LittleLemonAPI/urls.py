from django.urls import path, include
from .views import *

urlpatterns = [
    path('menu-items/', MenuItemList.as_view(), name="menuitem"),
    path('menu-items/<int:pk>/', MenuItemDetail.as_view(), name="menuitem-detail"),
    path('categories/', CategoryList.as_view(), name="category"),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name="category-detail"),
    path('cart/menu-items/', CartItemList.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'}), name="cartitem"),
    path('cart/menu-items/<int:pk>/', CartItemDetail.as_view(), name="cartitem-detail"),
    path('groups/manager/users/', ManagerUserList.as_view({'get': 'list', 'post': 'create'}), name="manager"),
    path('', include('djoser.urls')),
]
