from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


from datetime import datetime

from .models import blogModel
from .serializers import BlogDetailSerializer, BlogListSerializer

# Create your views here.

class BlogViewSet(viewsets.ModelViewSet):
    blog = blogModel
    queryset = blog.objects.all()
    authentication_classes = (TokenAuthentication, )
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return self.queryset
            return self.queryset.filter(status=1)
        return None
    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = BlogListSerializer
        else:
            serializer_class = BlogDetailSerializer
        return serializer_class
        