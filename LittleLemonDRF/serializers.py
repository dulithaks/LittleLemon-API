# restaurant/serializers.py
from rest_framework import serializers
from .models import Cart, MenuItem, Order, OrderItem

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
        
class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    
    class Meta:
        model = Order
        fields = '__all__'