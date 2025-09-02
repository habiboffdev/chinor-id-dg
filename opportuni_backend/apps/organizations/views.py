from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMember
from .serializers import (
    OrganizationSerializer, OrganizationUpdateSerializer,
    OrganizationMemberSerializer, OrganizationDashboardSerializer
)

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
        organization = get_object_or_404(Organization, user=self.request.user)
        return OrganizationMember.objects.filter(organization=organization)
    
    def perform_create(self, serializer):
        organization = get_object_or_404(Organization, user=self.request.user)
        serializer.save(organization=organization)


class OrganizationMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        organization = get_object_or_404(Organization, user=self.request.user)
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
