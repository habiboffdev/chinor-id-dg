from rest_framework import generics, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from .models import EmailTemplate, Message, BulkEmail, MessageThread
from .serializers import (
    EmailTemplateSerializer, MessageSerializer, MessageCreateSerializer,
    BulkEmailSerializer, MessageThreadSerializer, BulkEmailRequestSerializer, BulkEmailResponseSerializer
)
from apps.organizations.models import Organization


class EmailTemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return EmailTemplate.objects.none()
            
        if self.request.user.user_type == 'organization':
            try:
                organization = Organization.objects.get(user=self.request.user)
                return EmailTemplate.objects.filter(organization=organization)
            except Organization.DoesNotExist:
                return EmailTemplate.objects.none()
        return EmailTemplate.objects.none()
    
    def perform_create(self, serializer):
        organization = get_object_or_404(Organization, user=self.request.user)
        serializer.save(organization=organization)


class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return EmailTemplate.objects.none()
            
        if self.request.user.user_type == 'organization':
            try:
                organization = Organization.objects.get(user=self.request.user)
                return EmailTemplate.objects.filter(organization=organization)
            except Organization.DoesNotExist:
                return EmailTemplate.objects.none()
        return EmailTemplate.objects.none()


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Message.objects.none()
            
        user = self.request.user
        return Message.objects.filter(
            models.Q(sender=user) | models.Q(recipient=user)
        ).order_by('-sent_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessageDetailView(generics.RetrieveAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Message.objects.none()
            
        user = self.request.user
        return Message.objects.filter(
            models.Q(sender=user) | models.Q(recipient=user)
        )


@extend_schema(
    operation_id="communications_mark_message_as_read",
    summary="Mark Message as Read",
    description="Mark a specific message as read for the authenticated user",
    responses={
        200: MessageSerializer,
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Message not found"),
    },
    tags=["communications"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_message_as_read(request, pk):
    """Mark a message as read"""
    try:
        message = get_object_or_404(
            Message, 
            pk=pk, 
            recipient=request.user
        )
        
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Message.DoesNotExist:
        return Response(
            {'error': 'Message not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="communications_send_bulk_email",
    summary="Send Bulk Email",
    description="Send bulk email to multiple recipients (organizations only)",
    request=BulkEmailRequestSerializer,
    responses={
        201: BulkEmailResponseSerializer,
        400: OpenApiResponse(description="Bad request - missing required fields"),
        403: OpenApiResponse(description="Only organizations allowed"),
        404: OpenApiResponse(description="Organization not found"),
    },
    tags=["communications"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_bulk_email(request):
    """Send bulk email to multiple recipients"""
    if request.user.user_type != 'organization':
        return Response(
            {'error': 'Only organizations can send bulk emails'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        organization = Organization.objects.get(user=request.user)
        
        template_id = request.data.get('template_id')
        subject = request.data.get('subject')
        body = request.data.get('body')
        recipient_ids = request.data.get('recipient_ids', [])
        
        if not subject or not body or not recipient_ids:
            return Response(
                {'error': 'Subject, body, and recipient_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create bulk email record
        bulk_email = BulkEmail.objects.create(
            organization=organization,
            template_id=template_id if template_id else None,
            subject=subject,
            body=body,
            recipients=recipient_ids
        )
        
        # Start background task to send emails
        from apps.core.tasks import send_bulk_emails
        send_bulk_emails.delay(bulk_email.id, recipient_ids, subject, body)
        
        serializer = BulkEmailSerializer(bulk_email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
