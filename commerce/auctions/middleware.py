from .models import PageVisited, Listing
from django.shortcuts import get_object_or_404


class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.path.startswith("/listing/"):
            PageVisited.objects.create(user=request.user, path=request.path)

        return response
