# restaurant/serializers.py
from rest_framework import serializers
from .models import Cart, MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        
        
class CartSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ('user', 'unit_price', 'price')