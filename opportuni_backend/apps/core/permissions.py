from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is an organization member.
    """
    def has_permission(self, request, view):
        return request.user.user_type == 'organization'


class IsStudentUser(permissions.BasePermission):
    """
    Permission to check if user is a student.
    """
    def has_permission(self, request, view):
        return request.user.user_type == 'student'


class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission to check if user owns the organization.
    """
    def has_object_permission(self, request, view, obj):
        # For organization-related objects, check if user owns the organization
        if hasattr(obj, 'organization'):
            return obj.organization.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class CanManageApplications(permissions.BasePermission):
    """
    Permission to check if user can manage applications.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Students can only view/manage their own applications
        if user.user_type == 'student':
            return hasattr(obj, 'student') and obj.student.user == user
        
        # Organizations can manage applications to their opportunities
        elif user.user_type == 'organization':
            if hasattr(obj, 'opportunity'):
                return obj.opportunity.organization.user == user
            elif hasattr(obj, 'organization'):
                return obj.organization.user == user
        
        # Admins can manage all applications
        elif user.user_type == 'admin':
            return True
        
        return False
