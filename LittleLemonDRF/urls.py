from rest_framework.routers import DefaultRouter 
from .views import MenuItemViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')

urlpatterns = router.urls