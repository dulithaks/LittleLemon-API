from django.shortcuts import render

# Create your views here.
# restaurant/views.py
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsCustomer, IsManager, IsDeliveryCrew
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Cart, MenuItem, Order
from .serializers import CartSerializer, MenuItemSerializer, OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return [AllowAny()]
    
class GroupManagerUsersView(APIView):
    permission_classes = [IsManager]
    group_name = 'Manager'
    
    def _serialize_user(self, user):
        return {'id': user.id, 'username': user.username, 'email': user.email or ''}


    def get(self, request):
        group = Group.objects.filter(name=self.group_name).first()
        users = group.user_set.all() if group else []
        return Response([self._serialize_user(u) for u in users], status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.filter(id=request.data.get('user_id')).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(user)
        return Response(self._serialize_user(user), status=status.HTTP_201_CREATED)
    
    def delete(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        group = Group.objects.get(name=self.group_name)
        group.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
    
    
class GroupDeliveryCrewUsersView(APIView):
    permission_classes = [IsManager]
    group_name = 'Delivery Crew'
    
    def _serialize_user(self, user):
        return {'id': user.id, 'username': user.username, 'email': user.email or ''}


    def get(self, request):
        group = Group.objects.filter(name=self.group_name).first()
        users = group.user_set.all() if group else []
        return Response([self._serialize_user(u) for u in users], status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.filter(id=request.data.get('user_id')).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(user)
        return Response(self._serialize_user(user), status=status.HTTP_201_CREATED)
    
    def delete(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        group = Group.objects.get(name=self.group_name)
        group.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
    
class CartView(APIView):
    permission_classes = [IsCustomer]
    serializer_class = CartSerializer

    def get(self, request):
        user = request.user
        menu_items = Cart.objects.filter(user=user)
        serializer = self.serializer_class(menu_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CartSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else: 
            data = serializer.validated_data
            user = request.user
            menuitem = data.get('menuitem')
            quantity = data.get('quantity')

        cart_item, created = Cart.objects.update_or_create(
            user=user,
            menuitem=menuitem,
            defaults={
                "quantity": quantity,
                "unit_price": menuitem.price,
                "price": menuitem.price * quantity,
            }
        )
        serializer = self.serializer_class(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get(self, request):
        user = request.user
        if IsCustomer().has_permission(request, self):
            orders = Order.objects.filter(user=user)
        elif IsDeliveryCrew().has_permission(request, self):
            orders = Order.objects.filter(delivery_crew=user)
        elif IsManager().has_permission(request, self):
            orders = Order.objects.all()
        else:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(self.serializer_class(orders, many=True).data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
        if not IsCustomer().has_permission(request, self):
            return Response({'detail': 'Only customers can place orders.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get cart items for the user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total from cart items
        total = sum(item.price for item in cart_items)
        
        # Create the order
        from datetime import date
        order = Order.objects.create(
            user=user,
            total=total,
            date=date.today(),
            status=False
        )
        
        # Create order items from cart items
        from .models import OrderItem
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
        
        # Delete all cart items for this user
        cart_items.delete()
        
        # Return the created order with order items
        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)