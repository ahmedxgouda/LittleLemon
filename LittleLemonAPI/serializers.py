from rest_framework import serializers
from .models import *
import bleach

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReadMenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category']
        depth = 1
        
    
class WriteMenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category_id']
        
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
        
    