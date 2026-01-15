from django.shortcuts import render

# Create your views here.
# restaurant/views.py
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsManager, IsDeliveryCrew
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import MenuItem
from .serializers import MenuItemSerializer

class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return [AllowAny()]