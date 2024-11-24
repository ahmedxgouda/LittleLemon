from django.urls import path, include
from .views import MenuItemList, CategoryList, CategoryDetail, MenuItemDetail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('menu-items', MenuItemList.as_view(), name="menuitem"),
    path('menu-items/<int:pk>', MenuItemDetail.as_view(), name="menuitem-detail"),
    path('categories', CategoryList.as_view(), name="category"),
    path('categories/<int:pk>', CategoryDetail.as_view(), name="category-detail"),
    path('', include('djoser.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
