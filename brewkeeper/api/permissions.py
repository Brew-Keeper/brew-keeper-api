from rest_framework import permissions
import re


class IsAskerOrPublic(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        pub = re.search(r'^(/api/users/public/recipes/\d*/)', request.path)
        if request.method in permissions.SAFE_METHODS or \
                request.method == 'POST':
            try:
                pub.group(0)
                if '/api/users/public/recipes/' in pub.group(0):
                    return True
            except:
                return obj.user == request.user

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user
