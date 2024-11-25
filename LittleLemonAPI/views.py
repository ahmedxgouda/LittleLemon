from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import MenuItem, Category, CartItem
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group
from .permissions import *
# Create your views here.

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all()
    ordering_fields = ['title']
    search_fields = ['title']
    serializer_class = CategorySerializer
    permission_classes = [OnlyManagerCreates]

    
class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [OnlyManagerUpdates, OnlyManagerDestroys]
    
class MenuItemList(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    ordering_fields = ['title', 'featured']
    search_fields = ['title']
    filter_fields = ['category', 'featured']
    permission_classes = [OnlyManagerCreates]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadMenuItemSerializer
        else:
            return WriteMenuItemSerializer

    
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
    
class ManagerUserList(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    
    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        return AssignUserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data['username'])
        group = Group.objects.get(name='Manager')
        user.groups.add(group)
        return Response(status=status.HTTP_201_CREATED)

class RemoveManager(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = Group.objects.get(name='Manager')
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)
        
class DeliveryCrewList(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    
    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery crew')
      
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        return AssignUserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data['username'])
        group = Group.objects.get(name='Delivery crew')
        user.groups.add(group)
        return Response(status=status.HTTP_201_CREATED)

class RemoveDeliveryCrew(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = Group.objects.get(name='Delivery crew')
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)

class OrderList(ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOrderSerializer
        return WriteOrderSerializer
    
    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        if self.request.user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user)
        return Order.objects.filter(user=self.request.user)
    
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = CartItem.objects.filter(user=self.request.user)
        total = sum([item.price for item in items])
        if total != serializer.validated_data['total']:
            raise serializers.ValidationError("Total does not match cart total")
        order = Order.objects.create(user=self.request.user, total=total, status=False, date=serializer.validated_data['date'])
        order.save()
        for item in items:
            OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
        items.delete()
        return Response(status=status.HTTP_201_CREATED)
    

class OrderDetail(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [OnlyCustomerUpdates, DeliveryCrewOnlyPatchesStatus, ManagerUserOnlyPatchesStatusAndCrew, OnlyManagerDestroys] 

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return WriteOrderSerializer
    
    def retrieve(self, request, *args, **kwargs):
        is_manager = self.request.user.groups.filter(name='Manager').exists()
        is_delivery_crew = self.request.user.groups.filter(name='Delivery crew').exists()
        if not is_manager and not is_delivery_crew:
            if self.get_object().user != self.request.user:
                raise PermissionDenied("Customers only view their own orders", code=403)
        elif is_delivery_crew:
            if self.get_object().delivery_crew != self.request.user:
                raise PermissionDenied("Delivery crew only view their own orders", code=403)
        return super().retrieve(request, *args, **kwargs)
