from rest_framework import serializers
from .models import *
import bleach
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    email = serializers.EmailField(required=True)
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name')
        
class CustomUserSerializer(UserSerializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    email = serializers.EmailField(required=True)
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        
class AssignUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username']
        
    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReadMenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1
        
    
class WriteMenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category_id']
        
    def validate_title(self, value):
        return bleach.clean(value)
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
        
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
    
class ReadCartItemSerializer(serializers.ModelSerializer):
    menuitem = ReadMenuItemSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        depth = 1
        
class WriteCartItemSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'menuitem_id', 'quantity', 'unit_price', 'price', 'user_id']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=CartItem.objects.all(),
                fields=['user_id', 'menuitem_id'],
                message="You already have this item in your cart"
            )
        ]
        
    def validate(self, attrs):
        if attrs['quantity'] < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        if attrs['unit_price'] < 0:
            raise serializers.ValidationError("Price cannot be negative")
        if attrs['price'] != attrs['quantity'] * attrs['unit_price']:
            raise serializers.ValidationError("Price does not match quantity * unit price")
        menuitem = get_object_or_404(MenuItem, pk=attrs['menuitem_id'])
        if menuitem.price != attrs['unit_price']:
            raise serializers.ValidationError("Unit price does not match menu item price")
        return attrs
        
        
class ReadOrderItemSerializer(serializers.ModelSerializer):
    menuitem = ReadMenuItemSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price', 'order']
        depth = 1

class ReadOrderSerializer(serializers.ModelSerializer):
    order_items = ReadOrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'total', 'status', 'date', 'delivery_crew', 'order_items']
        
        
        
class WriteOrderItemSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem_id', 'quantity', 'unit_price', 'price']
        
    def validate(self, attrs):
        if attrs['quantity'] < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        if attrs['unit_price'] < 0:
            raise serializers.ValidationError("Price cannot be negative")
        if attrs['price'] != attrs['quantity'] * attrs['unit_price']:
            raise serializers.ValidationError("Price does not match quantity * unit price")
        menuitem = get_object_or_404(MenuItem, pk=attrs['menuitem_id'])
        if menuitem.price != attrs['unit_price']:
            raise serializers.ValidationError("Unit price does not match menu item price")
        return attrs
    
class WriteOrderSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Order
        fields = ['id', 'total', 'date']
        
    def validate(self, attrs):
        if attrs['total'] < 0:
            raise serializers.ValidationError("Total cannot be negative")
        if attrs['date'] < timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the past")
        return attrs