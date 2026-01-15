from django.shortcuts import render

# Create your views here.
# restaurant/views.py
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsManager, IsDeliveryCrew
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import MenuItem
from .serializers import MenuItemSerializer
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