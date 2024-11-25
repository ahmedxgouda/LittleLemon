from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery crew').exists()

class OnlyManagerCreates(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.groups.filter(name='Manager').exists()
        return True
    
class OnlyManagerUpdates(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PUT':
            return request.user.groups.filter(name='Manager').exists()
        return True
    
class OnlyManagerPatches(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PATCH':
            return request.user.groups.filter(name='Manager').exists()
        return True

class OnlyManagerDestroys(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user.groups.filter(name='Manager').exists()
        return True
    
class OnlyCustomerUpdates(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PUT':
            return not (request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery crew').exists())
        return True
    
class DeliveryCrewOnlyPatchesStatus(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PATCH':
            if request.user.groups.filter(name='Delivery crew').exists():
                return len(request.data) == 1 and 'status' in request.data
        return True
                
class ManagerUserOnlyPatchesStatusAndCrew(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'PATCH':
            if request.user.groups.filter(name='Manager').exists():
                if len(request.data) == 1:
                    return 'status' in request.data or 'delivery_crew_id' in request.data
                elif len(request.data) == 2:
                    return 'delivery_crew_id' in request.data and 'status' in request.data
        return True
    
