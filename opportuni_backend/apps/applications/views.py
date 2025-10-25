from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory, ApplicationAnswer
from .serializers import (
    ApplicationSerializer, ApplicationCreateSerializer, ApplicationUpdateSerializer,
    ApplicationListSerializer, ApplicationDocumentSerializer, ApplicationNoteSerializer,
    BulkStatusUpdateSerializer, ApplicationDocumentUploadSerializer, ApplicationDocumentUploadResponseSerializer
)
from apps.students.models import StudentProfile
from apps.organizations.models import Organization
from apps.opportunities.models import Opportunity
import django_filters


def _get_user_type(user):
    return getattr(user, 'user_type', None)


class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.MultipleChoiceFilter(choices=Application.STATUS_CHOICES)
    applied_after = django_filters.DateTimeFilter(field_name='applied_at', lookup_expr='gte')
    applied_before = django_filters.DateTimeFilter(field_name='applied_at', lookup_expr='lte')
    opportunity_type = django_filters.CharFilter(field_name='opportunity__opportunity_type')
    student_university = django_filters.CharFilter(field_name='student__university', lookup_expr='icontains')
    
    class Meta:
        model = Application
        fields = ['status', 'opportunity_type']


class ApplicationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ['student__user__first_name', 'student__user__last_name', 'opportunity__title']
    ordering_fields = ['applied_at', 'updated_at', 'status']
    ordering = ['-applied_at']
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Application.objects.none()
            
        user = self.request.user
        
        # Students see their own applications
        if _get_user_type(user) == 'student': 
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return Application.objects.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Application.objects.none()
        
        # Organizations see applications to their opportunities
        elif _get_user_type(user) == 'organization':
            try:
                organization = Organization.objects.get(user=user)
                return Application.objects.filter(opportunity__organization=organization)
            except Organization.DoesNotExist:
                return Application.objects.none()
        
        # Admins see all applications
        return Application.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationCreateSerializer
        return ApplicationListSerializer
    
    def perform_create(self, serializer):
        """
        🔴 CRITICAL: Create application with validated data
        Serializer already validates:
        - Required questions are answered
        - Answers are not empty
        - Profile requirements are met
        """
        # Get student profile
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            raise ValidationError({"student": "Talaba profili topilmadi."})
        
        # Save application with student profile
        # The serializer.create() method handles answers creation
        application = serializer.save(student=student_profile)


class OrganizationApplicationListView(generics.ListAPIView):
    """List applications scoped to the current organization with filters."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ['student__user__first_name', 'student__user__last_name', 'opportunity__title']
    ordering_fields = ['applied_at', 'updated_at', 'status']
    ordering = ['-applied_at']

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Application.objects.none()

        if _get_user_type(self.request.user) != 'organization':
            return Application.objects.none()
        try:
            organization = Organization.objects.get(user=self.request.user)
        except Organization.DoesNotExist:
            return Application.objects.none()
        qs = Application.objects.filter(opportunity__organization=organization)
        # Additional shortcut filter by opportunity id
        opp_id = self.request.query_params.get('opportunity')
        if opp_id:
            qs = qs.filter(opportunity_id=opp_id)
        return qs


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Application.objects.none()
            
        user = self.request.user
        
        # Students can access their own applications
        if _get_user_type(user) == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return Application.objects.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Application.objects.none()
        
        # Organizations can access applications to their opportunities
        elif _get_user_type(user) == 'organization':
            try:
                organization = Organization.objects.get(user=user)
                return Application.objects.filter(opportunity__organization=organization)
            except Organization.DoesNotExist:
                return Application.objects.none()
        
        # Admins can access all applications
        return Application.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Only organizations can update applications
            if _get_user_type(self.request.user) == 'organization':
                return ApplicationUpdateSerializer
            return ApplicationSerializer
        return ApplicationSerializer
    
    def update(self, request, *args, **kwargs):
        # Only organizations can update application status
        if _get_user_type(request.user) != 'organization':
            return Response(
                {'error': 'Only organizations can update application status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        application = self.get_object()
        old_status = application.status
        
        response = super().update(request, *args, **kwargs)
        
        # Create status history entry
        if response.status_code == 200:
            new_status = request.data.get('status')
            if new_status and new_status != old_status:
                ApplicationStatusHistory.objects.create(
                    application=application,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    reason=request.data.get('reason', '')
                )
        
        return response


class ApplicationDocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        application_id = self.kwargs.get('application_id')
        return ApplicationDocument.objects.filter(application_id=application_id)
    
    def perform_create(self, serializer):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(Application, id=application_id)
        
        # Check permissions
        user = self.request.user
        if _get_user_type(user) == 'student' and application.student.user != user:
            raise permissions.PermissionDenied("You can only upload documents to your own applications")
        elif _get_user_type(user) == 'organization':
            if not application.opportunity.organization.user == user:
                raise permissions.PermissionDenied("You can only access applications to your opportunities")
        
        serializer.save(application=application)


class ApplicationNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ApplicationNote.objects.none()
            
        application_id = self.kwargs.get('application_id')
        user = self.request.user
        
        # Students only see non-internal notes
        if _get_user_type(user) == 'student':
            return ApplicationNote.objects.filter(
                application_id=application_id,
                is_internal=False
            )
        
        # Organizations see all notes for their applications
        return ApplicationNote.objects.filter(application_id=application_id)
    
    def perform_create(self, serializer):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(Application, id=application_id)
        
        # Check permissions
        user = self.request.user
        if _get_user_type(user) == 'student' and application.student.user != user:
            raise permissions.PermissionDenied("You can only add notes to your own applications")
        elif _get_user_type(user) == 'organization':
            if not application.opportunity.organization.user == user:
                raise permissions.PermissionDenied("You can only add notes to applications for your opportunities")
        
        serializer.save(application=application, author=user)


@extend_schema(
    operation_id='withdraw_application',
    description='Withdraw a student application',
    request=None,
    responses={
        200: ApplicationSerializer,
        400: OpenApiResponse(description='Invalid operation'),
        404: OpenApiResponse(description='Application not found'),
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def withdraw_application(request, pk):
    """Withdraw an application"""
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        application = get_object_or_404(Application, pk=pk, student=student_profile)
        
        if application.status == 'withdrawn':
            return Response(
                {'error': 'Application is already withdrawn'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if application.status in ['accepted', 'rejected']:
            return Response(
                {'error': 'Cannot withdraw an application that has been accepted or rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = application.status
        application.status = 'withdrawn'
        application.save()
        
        # Create status history
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=old_status,
            new_status='withdrawn',
            changed_by=request.user,
            reason='Withdrawn by student'
        )
        
        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except StudentProfile.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id='bulk_update_application_status',
    description='Bulk update application status for organization',
    request=BulkStatusUpdateSerializer,
    responses={
        200: OpenApiResponse(description='Applications updated successfully'),
        400: OpenApiResponse(description='Invalid data'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_status(request):
    """Bulk update application status (for organizations)"""
    if _get_user_type(request.user) != 'organization':
        return Response(
            {'error': 'Only organizations can bulk update application status'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = BulkStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            organization = Organization.objects.get(user=request.user)
            application_ids = serializer.validated_data['application_ids']
            new_status = serializer.validated_data['status']
            reason = serializer.validated_data.get('reason', '')
            
            # Get applications that belong to this organization
            applications = Application.objects.filter(
                id__in=application_ids,
                opportunity__organization=organization
            )
            
            updated_count = 0
            for application in applications:
                old_status = application.status
                application.status = new_status
                application.updated_at = timezone.now()
                application.save()
                
                # Create status history
                ApplicationStatusHistory.objects.create(
                    application=application,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    reason=reason
                )
                updated_count += 1
            
            return Response(
                {'message': f'Successfully updated {updated_count} applications'},
                status=status.HTTP_200_OK
            )
            
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='get_application_stats',
    description='Get application statistics for organization',
    responses={
        200: OpenApiResponse(description='Application statistics'),
        403: OpenApiResponse(description='Only organizations allowed'),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def application_stats(request):
    """Get application statistics"""
    user = request.user
    
    user_type = _get_user_type(user)
    if user_type == 'student':
        try:
            student_profile = StudentProfile.objects.get(user=user)
            applications = Application.objects.filter(student=student_profile)
            
            stats = {
                'total_applications': applications.count(),
                'pending_applications': applications.filter(status='pending').count(),
                'under_review_applications': applications.filter(status='under_review').count(),
                'interview_scheduled': applications.filter(status='interview_scheduled').count(),
                'accepted_applications': applications.filter(status='accepted').count(),
                'rejected_applications': applications.filter(status='rejected').count(),
                'withdrawn_applications': applications.filter(status='withdrawn').count(),
            }
            
        except StudentProfile.DoesNotExist:
            stats = {'error': 'Student profile not found'}
    
    elif user_type == 'organization':
        try:
            organization = Organization.objects.get(user=user)
            applications = Application.objects.filter(opportunity__organization=organization)
            
            stats = {
                'total_applications': applications.count(),
                'pending_applications': applications.filter(status='pending').count(),
                'under_review_applications': applications.filter(status='under_review').count(),
                'interview_scheduled': applications.filter(status='interview_scheduled').count(),
                'accepted_applications': applications.filter(status='accepted').count(),
                'rejected_applications': applications.filter(status='rejected').count(),
                'withdrawn_applications': applications.filter(status='withdrawn').count(),
            }
            
        except Organization.DoesNotExist:
            stats = {'error': 'Organization profile not found'}
    
    else:
        stats = {'error': 'Invalid user type'}
    
    return Response(stats, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="applications_upload_document",
    summary="Upload Application Document",
    description="Upload a document file for applications (temporary storage until linked to specific application)",
    request=ApplicationDocumentUploadSerializer,
    responses={
        201: ApplicationDocumentUploadResponseSerializer,
        400: OpenApiResponse(description="Bad request - invalid file type or size"),
        401: OpenApiResponse(description="Authentication required"),
        500: OpenApiResponse(description="File upload failed"),
    },
    tags=["applications"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_application_document(request):
    """Upload a document for application"""
    print(f"Upload request received from user: {request.user}")
    print(f"Request FILES: {request.FILES}")
    print(f"Request data: {request.data}")
    
    if 'file' not in request.FILES:
        print("No file in request.FILES")
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    print(f"File received: {file.name}, size: {file.size}, content_type: {file.content_type}")
    
    # Validate file size (10MB limit)
    if file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'File size too large (max 10MB)'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file type
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'image/jpeg',
        'image/jpg',
        'image/png'
    ]
    
    if file.content_type not in allowed_types:
        print(f"Invalid file type: {file.content_type}")
        return Response(
            {'error': 'Invalid file type. Allowed: PDF, DOC, DOCX, TXT, JPG, PNG'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create temporary document record (will be linked to application later)
        from django.core.files.storage import default_storage
        import uuid
        
        # Generate unique filename
        file_extension = file.name.split('.')[-1] if '.' in file.name else ''
        unique_filename = f"application_docs/{uuid.uuid4()}.{file_extension}"
        
        # Save file
        file_path = default_storage.save(unique_filename, file)
        file_url = default_storage.url(file_path)
        
        print(f"File saved successfully: {file_path}")
        print(f"File URL: {file_url}")
        
        return Response({
            'file_url': file_url,
            'filename': file.name,
            'size': file.size,
            'content_type': file.content_type
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return Response(
            {'error': f'Failed to upload file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="applications_check_status",
    summary="Check Application Status",
    description="Check if the current student has already applied to a specific opportunity",
    responses={
        200: ApplicationListSerializer,
        403: OpenApiResponse(description="Only students allowed"),
        404: OpenApiResponse(description="Student profile not found"),
    },
    tags=["applications"],
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_application_status(request, opportunity_id):
    """
    Check if the current user has already applied to a specific opportunity.
    Returns application details if found, or null if not found.
    """
    if _get_user_type(request.user) != 'student':
        return Response({'error': 'Only students can check application status'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        application = Application.objects.filter(
            student=student_profile,
            opportunity_id=opportunity_id
        ).first()
        
        if application:
            serializer = ApplicationListSerializer(application)
            return Response(serializer.data)
        else:
            return Response(None)
            
    except StudentProfile.DoesNotExist:
        return Response({'error': 'Student profile not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
