from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Opportunity, OpportunityCategory
from .serializers import (
    OpportunitySerializer, OpportunityCreateUpdateSerializer,
    OpportunityListSerializer, OpportunityCategorySerializer
)
from apps.organizations.models import Organization
import django_filters
from django.db import models


class OpportunityFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    opportunity_type = django_filters.MultipleChoiceFilter(choices=Opportunity.OPPORTUNITY_TYPES)
    status = django_filters.MultipleChoiceFilter(choices=Opportunity.STATUS_CHOICES)
    min_gpa = django_filters.NumberFilter(field_name='min_gpa', lookup_expr='lte')
    is_remote = django_filters.BooleanFilter()
    featured = django_filters.BooleanFilter()
    deadline_after = django_filters.DateTimeFilter(field_name='application_deadline', lookup_expr='gte')
    is_active = django_filters.BooleanFilter(method='filter_is_active')
    
    class Meta:
        model = Opportunity
        fields = ['title', 'location', 'opportunity_type', 'status', 'is_remote', 'featured']

    def filter_is_active(self, queryset, name, value):
        """Active means not closed/cancelled and deadline in the future."""
        if value is None:
            return queryset
        now = timezone.now()
        if value:
            return queryset.exclude(status__in=['closed', 'cancelled']).filter(application_deadline__gt=now)
        return queryset.filter(models.Q(status__in=['closed', 'cancelled']) | models.Q(application_deadline__lte=now))


class OpportunityListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OpportunityFilter
    search_fields = ['title', 'description', 'location', 'organization__name']
    ordering_fields = ['created_at', 'application_deadline', 'title']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Allow GET requests without authentication for browsing opportunities
        Require authentication for POST (creating opportunities)
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        # If user is authenticated, apply role-based filtering
        if self.request.user.is_authenticated:
            # Students see only published opportunities
            if self.request.user.user_type == 'student':
                return Opportunity.objects.filter(
                    status='published',
                    application_deadline__gt=timezone.now()
                ).select_related('organization').prefetch_related('required_skills', 'requirements', 'additional_questions')
            
            # Organizations see their own opportunities
            elif self.request.user.user_type == 'organization':
                try:
                    organization = Organization.objects.get(user=self.request.user)
                    return Opportunity.objects.filter(
                        organization=organization
                    ).select_related('organization').prefetch_related('required_skills', 'requirements', 'additional_questions')
                except Organization.DoesNotExist:
                    return Opportunity.objects.none()
            
            # Admins see all opportunities
            return Opportunity.objects.all().select_related('organization').prefetch_related('required_skills', 'requirements', 'additional_questions')
        
        # For unauthenticated users, show only published opportunities
        return Opportunity.objects.filter(
            status='published',
            application_deadline__gt=timezone.now()
        ).select_related('organization').prefetch_related('required_skills', 'requirements', 'additional_questions')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OpportunityCreateUpdateSerializer
        return OpportunityListSerializer
    
    def perform_create(self, serializer):
        organization = get_object_or_404(Organization, user=self.request.user)
        serializer.save(organization=organization)


class OrganizationActiveOpportunitiesView(generics.ListAPIView):
    """
    Convenience endpoint for organizations to list their active opportunities
    (status not closed/cancelled and deadline in future). Supports pagination.
    """
    serializer_class = OpportunityListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'application_deadline']
    ordering = ['-created_at']

    def get_queryset(self):
        organization = get_object_or_404(Organization, user=self.request.user)
        qs = Opportunity.objects.filter(
            organization=organization,
        ).exclude(status__in=['closed', 'cancelled']).filter(
            application_deadline__gt=timezone.now()
        )
        # optional toggle by query param is_active=true/false
        is_active = self.request.query_params.get('is_active')
        if is_active in ('false', '0'):
            qs = Opportunity.objects.filter(organization=organization)
        return qs.select_related('organization')


class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    def get_permissions(self):
        """
        Allow GET requests without authentication for viewing opportunity details
        Require authentication for PUT/PATCH/DELETE
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        # If user is authenticated, apply role-based filtering
        if self.request.user.is_authenticated:
            # Students can view published opportunities
            if self.request.user.user_type == 'student':
                return Opportunity.objects.filter(status='published')
            
            # Organizations can manage their own opportunities
            elif self.request.user.user_type == 'organization':
                try:
                    organization = Organization.objects.get(user=self.request.user)
                    return Opportunity.objects.filter(organization=organization)
                except Organization.DoesNotExist:
                    return Opportunity.objects.none()
            
            # Admins can access all opportunities
            return Opportunity.objects.all()
        
        # For unauthenticated users, show only published opportunities
        return Opportunity.objects.filter(status='published')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OpportunityCreateUpdateSerializer
        return OpportunitySerializer


class OpportunitySearchView(generics.ListAPIView):
    serializer_class = OpportunityListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OpportunityFilter
    search_fields = ['title', 'description', 'location', 'organization__name']
    ordering_fields = ['created_at', 'application_deadline', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Opportunity.objects.filter(
            status='published',
            application_deadline__gt=timezone.now()
        ).select_related('organization')


class FeaturedOpportunitiesView(generics.ListAPIView):
    serializer_class = OpportunityListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Opportunity.objects.filter(
            status='published',
            featured=True,
            application_deadline__gt=timezone.now()
        ).select_related('organization')[:10]


class OpportunityCategoryListView(generics.ListAPIView):
    serializer_class = OpportunityCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OpportunityCategory.objects.filter(is_active=True)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def publish_opportunity(request, pk):
    """Publish an opportunity"""
    try:
        organization = Organization.objects.get(user=request.user)
        opportunity = get_object_or_404(Opportunity, pk=pk, organization=organization)
        
        if opportunity.status == 'published':
            return Response(
                {'error': 'Opportunity is already published'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        opportunity.status = 'published'
        opportunity.save()
        
        serializer = OpportunitySerializer(opportunity)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def close_opportunity(request, pk):
    """Close an opportunity"""
    try:
        organization = Organization.objects.get(user=request.user)
        opportunity = get_object_or_404(Opportunity, pk=pk, organization=organization)
        
        if opportunity.status == 'closed':
            return Response(
                {'error': 'Opportunity is already closed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        opportunity.status = 'closed'
        opportunity.save()
        
        serializer = OpportunitySerializer(opportunity)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def opportunity_stats(request):
    """Get opportunity statistics for organizations"""
    try:
        organization = Organization.objects.get(user=request.user)
        
        stats = {
            'total_opportunities': organization.opportunities.count(),
            'published_opportunities': organization.opportunities.filter(status='published').count(),
            'draft_opportunities': organization.opportunities.filter(status='draft').count(),
            'closed_opportunities': organization.opportunities.filter(status='closed').count(),
            'total_applications': sum(opp.application_count for opp in organization.opportunities.all()),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Organization profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_opportunities(request):
    """
    Debug endpoint to check opportunities status
    """
    user = request.user
    user_type = user.user_type
    total_opportunities = Opportunity.objects.count()
    published_opportunities = Opportunity.objects.filter(status='published').count()
    future_deadlines = Opportunity.objects.filter(application_deadline__gt=timezone.now()).count()
    
    # Check what the user would see based on the current filters
    if user_type == 'student':
        visible_opportunities = Opportunity.objects.filter(
            status='published',
            application_deadline__gt=timezone.now()
        ).count()
    elif user_type == 'organization':
        try:
            organization = Organization.objects.get(user=user)
            visible_opportunities = Opportunity.objects.filter(
                organization=organization
            ).count()
        except Organization.DoesNotExist:
            visible_opportunities = 0
            organization = None
    else:
        visible_opportunities = total_opportunities
    
    debug_info = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'user_type': user_type,
        'total_opportunities': total_opportunities,
        'published_opportunities': published_opportunities, 
        'future_deadlines': future_deadlines,
        'visible_opportunities': visible_opportunities,
    }
    
    if user_type == 'organization' and organization:
        debug_info['organization_id'] = organization.id
        debug_info['organization_name'] = organization.name
    
    # Add additional info about the first few opportunities
    sample_opportunities = []
    for opp in Opportunity.objects.all()[:5]:
        sample_opportunities.append({
            'id': opp.id,
            'title': opp.title,
            'status': opp.status,
            'deadline': opp.application_deadline,
            'is_deadline_passed': opp.application_deadline < timezone.now(),
            'organization_id': opp.organization_id,
        })
    
    debug_info['sample_opportunities'] = sample_opportunities
    
    return Response(debug_info)
