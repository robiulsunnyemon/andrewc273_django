from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit/delete it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD or OPTIONS request shobar jonno allow (Read-only)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permission shudhu owner-er jonno (Update/Delete)
        return obj.user == request.user