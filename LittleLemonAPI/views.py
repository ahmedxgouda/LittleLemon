from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import ReadMenuItemSerializer, WriteMenuItemSerializer, CategorySerializer
from .models import MenuItem, Category
from rest_framework.exceptions import PermissionDenied

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