from rest_framework import generics, status, permissions, filters
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from .models import Organization, OrganizationMember
from .serializers import (
    OrganizationSerializer, OrganizationUpdateSerializer,
    OrganizationMemberSerializer, OrganizationDashboardSerializer,
    LogoUploadSerializer, LogoUploadResponseSerializer,
    InviteMemberSerializer, InviteMemberResponseSerializer,
    InviteStudentsSerializer, InviteStudentsResponseSerializer,
    StudentStatsSerializer
)
from apps.applications.models import Application
from apps.students.models import StudentProfile
from apps.opportunities.models import Opportunity

User = get_user_model()


class OrganizationProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Organization, user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return OrganizationUpdateSerializer
        return OrganizationSerializer


class OrganizationDashboardView(generics.RetrieveAPIView):
    serializer_class = OrganizationDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Organization, user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Return dashboard payload aligned with frontend expectations.
        """
        org = self.get_object()
        data = self.get_serializer(org).data
        # Map keys for frontend compatibility (organization-dashboard.js expects these)
        payload = {
            'active_opportunities': data.get('total_opportunities', 0),
            'new_applications': data.get('total_applications', 0),
            'interviews_scheduled': data.get('interviews_scheduled', 0),
            'hires_month': data.get('accepted_applications', 0),
            'member_count': data.get('member_count', 0),
            'recent_applications': data.get('recent_applications', []),
        }
        return Response(payload)


# Organization Members Views
class OrganizationMemberListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return OrganizationMember.objects.none()
            
        return OrganizationMember.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        organization = get_object_or_404(Organization, user=self.request.user)
        serializer.save(organization=organization)


class OrganizationMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return OrganizationMember.objects.none()
            
        return OrganizationMember.objects.filter(organization=organization)


# Organization Search and List Views
class OrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Organization.objects.filter(is_active=True, is_verified=True)
        
        # Search by name or organization type
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        org_type = self.request.query_params.get('type', None)
        if org_type:
            queryset = queryset.filter(organization_type=org_type)
        
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country__icontains=country)
            
        return queryset


class OrganizationDetailView(generics.RetrieveAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.filter(is_active=True, is_verified=True)
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    operation_id="organization_upload_logo",
    summary="Upload Organization Logo",
    description="Upload a logo image for the organization",
    request=LogoUploadSerializer,
    responses={
        200: LogoUploadResponseSerializer,
        400: OpenApiResponse(description="Bad request - no logo file provided"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Organization profile not found"),
    },
    tags=["organizations"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_logo(request):
    """Upload organization logo"""
    try:
        organization = Organization.objects.get(user=request.user)
        if 'logo' in request.FILES:
            organization.logo = request.FILES['logo']
            organization.save()
            serializer = OrganizationSerializer(organization)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'No logo file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="organizations_invite_member",
    summary="Invite Member to Organization",
    description="Invite a user to join the organization by email",
    request=InviteMemberSerializer,
    responses={
        201: InviteMemberResponseSerializer,
        400: OpenApiResponse(description="Bad request - email required or user already member"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Organization or user not found"),
    },
    tags=["organizations"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invite_member(request):
    """Invite a user to join the organization"""
    try:
        organization = Organization.objects.get(user=request.user)
        email = request.data.get('email')
        role = request.data.get('role', 'viewer')
        
        if not email:
            return Response(
                {'error': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Check if user is already a member
            if OrganizationMember.objects.filter(organization=organization, user=user).exists():
                return Response(
                    {'error': 'User is already a member of this organization'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the membership
            member = OrganizationMember.objects.create(
                organization=organization,
                user=user,
                role=role
            )
            
            serializer = OrganizationMemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="organizations_get_student_stats",
    summary="Get Student Statistics",
    description="Get statistics about students who have applied to organization's opportunities",
    responses={
        200: StudentStatsSerializer,
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Organization not found"),
    },
    tags=["organizations"],
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_stats(request):
    """Get student statistics for organization"""
    try:
        organization = Organization.objects.get(user=request.user)
        
        # Get all applications to organization's opportunities
        org_opportunities = Opportunity.objects.filter(organization=organization)
        applications = Application.objects.filter(opportunity__in=org_opportunities)
        
        # Calculate stats
        total_students = applications.values('student').distinct().count()
        active_applicants = applications.filter(status='pending').values('student').distinct().count()
        hired_students = applications.filter(status='accepted').values('student').distinct().count()
        
        # New students this week
        week_ago = timezone.now() - timedelta(days=7)
        new_this_week = applications.filter(
            applied_at__gte=week_ago
        ).values('student').distinct().count()
        
        stats = {
            'total_students': total_students,
            'active_applicants': active_applicants,
            'hired_students': hired_students,
            'new_this_week': new_this_week
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="organizations_get_students",
    summary="Get Organization's Students",
    description="Get students who have applied to organization's opportunities",
    responses={
        200: OpenApiResponse(description="List of students with application details"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Organization not found"),
    },
    tags=["organizations"],
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_students(request):
    """Get students who have applied to organization's opportunities"""
    try:
        organization = Organization.objects.get(user=request.user)
        
        # Get all applications to organization's opportunities
        org_opportunities = Opportunity.objects.filter(organization=organization)
        applications = Application.objects.filter(opportunity__in=org_opportunities)
        
        # Get unique students with their latest application status
        student_ids = applications.values('student').distinct()
        students = StudentProfile.objects.filter(id__in=student_ids)
        
        # Apply filters
        search = request.GET.get('search', '')
        major = request.GET.get('major', '')
        year = request.GET.get('year', '')
        status_filter = request.GET.get('status', '')
        
        if search:
            students = students.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(university__icontains=search)
            )
        
        if major:
            students = students.filter(major__icontains=major)
            
        if year:
            students = students.filter(year__icontains=year)
        
        # Serialize student data with application status
        student_data = []
        for student in students:
            latest_app = applications.filter(student=student).order_by('-applied_at').first()
            student_info = {
                'id': student.id,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'email': student.user.email,
                'major': student.major,
                'year': student.year,
                'university': student.university,
                'status': latest_app.status if latest_app else 'unknown',
                'latest_application': latest_app.applied_at if latest_app else None
            }
            
            # Apply status filter
            if status_filter:
                if status_filter == 'active' and latest_app and latest_app.status == 'pending':
                    student_data.append(student_info)
                elif status_filter == 'applied' and latest_app:
                    student_data.append(student_info)
                elif status_filter == 'hired' and latest_app and latest_app.status == 'accepted':
                    student_data.append(student_info)
                elif not status_filter:
                    student_data.append(student_info)
            else:
                student_data.append(student_info)
        
        # Simple pagination
        page = int(request.GET.get('page', 1))
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size
        
        response_data = {
            'results': student_data[start:end],
            'count': len(student_data),
            'page': page,
            'page_size': page_size
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id="organizations_invite_students",
    summary="Invite Students to Opportunities",
    description="Send invitations to students to apply for opportunities",
    request=InviteStudentsSerializer,
    responses={
        200: InviteStudentsResponseSerializer,
        400: OpenApiResponse(description="Bad request - email list required"),
        401: OpenApiResponse(description="Authentication required"),
        404: OpenApiResponse(description="Organization not found"),
    },
    tags=["organizations"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invite_students(request):
    """Invite students to apply for opportunities"""
    try:
        organization = Organization.objects.get(user=request.user)
        emails = request.data.get('emails', [])
        message = request.data.get('message', '')
        
        if not emails:
            return Response(
                {'error': 'Email list is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Here you would typically send invitation emails
        # For now, just return success
        
        return Response({
            'message': f'Invitations sent to {len(emails)} students',
            'sent_count': len(emails)
        }, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
