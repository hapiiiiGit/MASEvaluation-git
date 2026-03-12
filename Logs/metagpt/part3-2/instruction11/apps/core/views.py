from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import CoreData
from .serializers import CoreDataSerializer

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class CoreDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on CoreData.
    Only authenticated users can access.
    Users can only access their own CoreData objects.
    """
    serializer_class = CoreDataSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Only return CoreData objects owned by the current user
        return CoreData.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Set the owner to the current user
        serializer.save(owner=self.request.user)

    def retrieve(self, request, pk=None):
        # Ensure user can only retrieve their own objects
        queryset = self.get_queryset()
        coredata = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, coredata)
        serializer = self.get_serializer(coredata)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # Ensure user can only update their own objects
        queryset = self.get_queryset()
        coredata = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, coredata)
        serializer = self.get_serializer(coredata, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        # Ensure user can only partially update their own objects
        queryset = self.get_queryset()
        coredata = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, coredata)
        serializer = self.get_serializer(coredata, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        # Ensure user can only delete their own objects
        queryset = self.get_queryset()
        coredata = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, coredata)
        coredata.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)