from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='Manager').exists()
        )


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Delivery Crew').exists()
    

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists()
