from rest_framework import serializers
from .models import *
import bleach
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404

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
    
    class Meta:
        model = CartItem
        fields = ['id', 'menuitem_id', 'quantity', 'unit_price', 'price', 'user']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=CartItem.objects.all(),
                fields=['user', 'menuitem_id'],
                message="You already have this item in your cart"
            )
        ]
        
    def create(self, validated_data):
        validated_data['price'] = validated_data['quantity'] * validated_data['unit_price']
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
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
        
        