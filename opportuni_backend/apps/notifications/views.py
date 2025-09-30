from rest_framework import generics, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification, NotificationSettings
from .serializers import NotificationSerializer, NotificationSettingsSerializer, MarkAllNotificationsReadResponseSerializer, NotificationStatsSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
            
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
            
        return Notification.objects.filter(recipient=self.request.user)


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        settings, created = NotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings


@extend_schema(
    operation_id="notifications_mark_as_read",
    summary="Mark Notification as Read",
    description="Mark a specific notification as read for the authenticated user",
    responses={
        200: NotificationSerializer,
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Notification not found"),
    },
    tags=["notifications"],
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_as_read(request, pk):
    """Mark a notification as read"""
    try:
        notification = get_object_or_404(
            Notification, 
            pk=pk, 
            recipient=request.user
        )
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="notifications_mark_all_as_read",
    summary="Mark All Notifications as Read",
    description="Mark all unread notifications as read for the authenticated user",
    responses={
        200: MarkAllNotificationsReadResponseSerializer,
        401: OpenApiResponse(description="Authentication required"),
    },
    tags=["notifications"],
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_as_read(request):
    """Mark all notifications as read for the current user"""
    updated = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response(
        {'message': f'Marked {updated} notifications as read'},
        status=status.HTTP_200_OK
    )


@extend_schema(
    operation_id="notifications_delete",
    summary="Delete Notification",
    description="Delete a specific notification for the authenticated user",
    responses={
        204: OpenApiResponse(description="Notification deleted successfully"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Notification not found"),
    },
    tags=["notifications"],
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, pk):
    """Delete a notification"""
    try:
        notification = get_object_or_404(
            Notification, 
            pk=pk, 
            recipient=request.user
        )
        notification.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="notifications_get_stats",
    summary="Get Notification Statistics",
    description="Get notification statistics for the authenticated user",
    responses={
        200: NotificationStatsSerializer,
        401: OpenApiResponse(description="Authentication required"),
    },
    tags=["notifications"],
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get notification statistics for the current user"""
    user_notifications = Notification.objects.filter(recipient=request.user)
    
    stats = {
        'total_notifications': user_notifications.count(),
        'unread_notifications': user_notifications.filter(is_read=False).count(),
        'notifications_by_type': {}
    }
    
    # Count notifications by type
    for notification_type, _ in Notification.NOTIFICATION_TYPES:
        count = user_notifications.filter(notification_type=notification_type).count()
        stats['notifications_by_type'][notification_type] = count
    
    return Response(stats, status=status.HTTP_200_OK)
