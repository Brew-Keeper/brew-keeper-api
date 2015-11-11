from rest_framework.authentication import SessionAuthentication as OriginalSessionAuthentication


class SessionAuthentication(OriginalSessionAuthentication):
    def enforce_csrf(self, request):
        return
