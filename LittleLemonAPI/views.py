from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import MenuItem, Category, CartItem
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group
from .permissions import *
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
# Create your views here.

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all()
    ordering_fields = ['title']
    search_fields = ['title']
    serializer_class = CategorySerializer
    permission_classes = [OnlyManagerCreates]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [OnlyManagerUpdates, OnlyManagerDestroys, OnlyManagerPatches]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
class MenuItemList(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    ordering_fields = ['title', 'featured']
    search_fields = ['title']
    filter_fields = ['category', 'featured']
    permission_classes = [OnlyManagerCreates]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadMenuItemSerializer
        else:
            return WriteMenuItemSerializer

    
class MenuItemDetail(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = ReadMenuItemSerializer
    permission_classes = [OnlyManagerUpdates, OnlyManagerDestroys, OnlyManagerPatches]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
class CartItemList(ModelViewSet):
    queryset = CartItem.objects.all()
    throttle_classes = [UserRateThrottle]
    
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
    throttle_classes = [UserRateThrottle]
    
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to perform this action", code=403)
        return super().destroy(request, *args, **kwargs)
    
class ManagerUserList(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        return AssignUserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        group = Group.objects.get(name='Manager')
        user.groups.add(group)
        return Response(status=status.HTTP_201_CREATED, data="Manager added")

class RemoveManager(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    throttle_classes = [UserRateThrottle]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = Group.objects.get(name='Manager')
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK, data="Manager removed")
        
class DeliveryCrewList(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    throttle_classes = [UserRateThrottle]
    
    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery crew')
      
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        return AssignUserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        group = Group.objects.get(name='Delivery crew')
        user.groups.add(group)
        return Response(status=status.HTTP_201_CREATED, data="Delivery crew added")

class RemoveDeliveryCrew(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    throttle_classes = [UserRateThrottle]
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = Group.objects.get(name='Delivery crew')
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK, data="Delivery crew removed")

class OrderList(ListCreateAPIView):
    ordering_fields = ['date', 'status']
    search_fields = ['date', 'status']
    filter_fields = ['status']
    throttle_classes = [UserRateThrottle]
    
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
        return Response(status=status.HTTP_201_CREATED, data="Order created")
    

class OrderDetail(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [OnlyCustomerUpdates, DeliveryCrewOnlyPatchesStatus, ManagerUserOnlyPatchesStatusAndCrew, OnlyManagerDestroys]
    throttle_classes = [UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOrderSerializer
        elif self.request.method == 'PATCH':
            return PatchOrderSerializer
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

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = CartItem.objects.filter(user=self.request.user)
        total = sum([item.price for item in items])
        if total != serializer.validated_data['total']:
            raise serializers.ValidationError("Total does not match cart total")
        order = self.get_object()
        order.total = total
        order.date = serializer.validated_data['date']
        order.save()
        OrderItem.objects.filter(order=order).delete()
        for item in items:
            OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
        items.delete()
        return Response(status=status.HTTP_200_OK, data="Order updated")
    
    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.get_object()
        if 'status' in serializer.validated_data:
            order.status = serializer.validated_data['status']
        if 'delivery_crew_id' in serializer.validated_data:
            order.delivery_crew = User.objects.get(id=serializer.validated_data['delivery_crew_id'])
        order.save()
        return Response(status=status.HTTP_200_OK, data="Order updated")
        
class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsManager]
    throttle_classes = [UserRateThrottle]
