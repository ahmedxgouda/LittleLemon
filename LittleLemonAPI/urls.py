from django.urls import path, include
from .views import MenuItemList, CategoryList, CategoryDetail, MenuItemDetail

urlpatterns = [
    path('menu-items/', MenuItemList.as_view(), name="menuitem"),
    path('menu-items/<int:pk>/', MenuItemDetail.as_view(), name="menuitem-detail"),
    path('categories/', CategoryList.as_view(), name="category"),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name="category-detail"),
    path('', include('djoser.urls')),
]
