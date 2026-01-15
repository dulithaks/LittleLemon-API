from rest_framework.routers import DefaultRouter 
from .views import GroupManagerUsersView, MenuItemViewSet
from django.urls import path

router = DefaultRouter(trailing_slash=False)
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')

urlpatterns = [
    path('groups/manager/users', GroupManagerUsersView.as_view()),
    path('groups/manager/users/<int:user_id>', GroupManagerUsersView.as_view()),
    # path('groups/delivery-crew/users', GroupUsersView.as_view()),
    # path('groups/delivery-crew/users/<int:user_id>', GroupUsersView.as_view()),
] + router.urls