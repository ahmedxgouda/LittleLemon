from django.urls import path, include
from .views import MenuItemList, CategoryList, CategoryDetail, MenuItemDetail, CartItemList, CartItemDetail

urlpatterns = [
    path('menu-items/', MenuItemList.as_view(), name="menuitem"),
    path('menu-items/<int:pk>/', MenuItemDetail.as_view(), name="menuitem-detail"),
    path('categories/', CategoryList.as_view(), name="category"),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name="category-detail"),
    path('cart/menu-items/', CartItemList.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'}), name="cartitem"),
    path('cart/menu-items/<int:pk>/', CartItemDetail.as_view(), name="cartitem-detail"),
    path('', include('djoser.urls')),
]
