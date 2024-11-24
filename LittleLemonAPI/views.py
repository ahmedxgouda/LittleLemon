from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import MenuItem, Category, CartItem
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all()
    ordering_fields = ['title']
    search_fields = ['title']
    serializer_class = CategorySerializer
    
    def create(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().create(request, *args, **kwargs)

    
class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def update(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().destroy(request, *args, **kwargs)
    
class MenuItemList(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    ordering_fields = ['title', 'featured']
    search_fields = ['title']
    filter_fields = ['category', 'featured']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadMenuItemSerializer
        else:
            return WriteMenuItemSerializer
        
    def create(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().create(request, *args, **kwargs)
    
class MenuItemDetail(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = ReadMenuItemSerializer
    
    def update(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not self.request.user.groups.filter(name='Manager').exists():
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().destroy(request, *args, **kwargs)
    
class CartItemList(ModelViewSet):
    queryset = CartItem.objects.all()
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteCartItemSerializer
        return ReadCartItemSerializer
    
    def create(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.id
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.queryset.filter(user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    
    
class CartItemDetail(DestroyAPIView):
    serializer_class = ReadCartItemSerializer
    queryset = CartItem.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().destroy(request, *args, **kwargs)
    
