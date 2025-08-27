from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import (
    StudentProfile, Education, Experience, Skill, StudentSkill, 
    Project, Achievement, Language, SocialLink
)
from .serializers import (
    StudentProfileSerializer, StudentProfileUpdateSerializer,
    EducationSerializer, ExperienceSerializer, SkillSerializer,
    StudentSkillSerializer, ProjectSerializer, AchievementSerializer,
    LanguageSerializer, StudentDashboardSerializer, SocialLinkSerializer
)

User = get_user_model()

def get_or_create_student_profile(user):
    """Helper function to safely get or create a StudentProfile with defaults"""
    profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone': '',
            'date_of_birth': None,
            'location': '',
            'bio': '',
            'university': '',
            'major': '',
            'graduation_year': None,
            'gpa': None,
            'resume': '',
            'portfolio_url': '',
            'about_me': ''
        }
    )
    return profile, created

class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = get_or_create_student_profile(self.request.user)
        return profile
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StudentProfileUpdateSerializer
        return StudentProfileSerializer
    
    def update(self, request, *args, **kwargs):
        print("=" * 50)
        print("PROFILE UPDATE REQUEST RECEIVED")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request data: {request.data}")
        print(f"Request files: {request.FILES}")
        print("=" * 50)
        
        try:
            result = super().update(request, *args, **kwargs)
            print("UPDATE SUCCESSFUL - Response data:", result.data)
            return result
        except Exception as e:
            print(f"UPDATE FAILED - Error: {e}")
            raise

class StudentDashboardView(generics.RetrieveAPIView):
    serializer_class = StudentDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = get_or_create_student_profile(self.request.user)
        return profile

# Education Views
class EducationListCreateView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Education.objects.filter(student=student_profile)
    
    def perform_create(self, serializer):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(student=student_profile)

class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Education.objects.filter(student=student_profile)

# Experience Views
class ExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Experience.objects.filter(student=student_profile)
    
    def perform_create(self, serializer):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(student=student_profile)

class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Experience.objects.filter(student=student_profile)

# Skills Views
class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class StudentSkillListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return StudentSkill.objects.filter(student=student_profile)
    
    def perform_create(self, serializer):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(student=student_profile)

class StudentSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return StudentSkill.objects.filter(student=student_profile)

# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Project.objects.filter(student=student_profile)
    
    def perform_create(self, serializer):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(student=student_profile)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Project.objects.filter(student=student_profile)

# Achievement Views
class AchievementListCreateView(generics.ListCreateAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Achievement.objects.filter(student=student_profile)
    
    def perform_create(self, serializer):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(student=student_profile)

class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Achievement.objects.filter(student=student_profile)

# Language Views
class LanguageListCreateView(generics.ListCreateAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Language.objects.filter(student=student_profile)
    
    def perform_create(self, serializer):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        serializer.save(student=student_profile)

class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Language.objects.filter(student=student_profile)

# Social Links Views
class SocialLinkListCreateView(generics.ListCreateAPIView):
    serializer_class = SocialLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student_profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return SocialLink.objects.filter(student=student_profile)

    def perform_create(self, serializer):
        student_profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        serializer.save(student=student_profile)


class SocialLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SocialLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student_profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return SocialLink.objects.filter(student=student_profile)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upsert_social_link(request):
    """Create or update a single social link by platform for the current student."""
    try:
        student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        platform = request.data.get('platform')
        url = request.data.get('url')
        label = request.data.get('label', '')
        is_public = request.data.get('is_public', True)
        sort_order = request.data.get('sort_order', 0)

        if not platform or not url:
            return Response({'detail': 'platform and url are required'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = SocialLink.objects.update_or_create(
            student=student_profile,
            platform=platform,
            defaults={
                'url': url,
                'label': label,
                'is_public': bool(is_public),
                'sort_order': int(sort_order) if str(sort_order).isdigit() else 0,
            }
        )
        ser = SocialLinkSerializer(obj)
        return Response(ser.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': f'Failed to upsert social link: {e}'}, status=status.HTTP_400_BAD_REQUEST)

# Resume Upload View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_resume(request):
    """Upload resume file for student"""
    student_profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )
    
    if 'resume' not in request.FILES:
        return Response({'error': 'No resume file provided'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    resume_file = request.FILES['resume']
    
    # Validate file type
    allowed_types = ['application/pdf', 'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if resume_file.content_type not in allowed_types:
        return Response({'error': 'Only PDF and Word documents are allowed'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (5MB max)
    if resume_file.size > 5 * 1024 * 1024:
        return Response({'error': 'File size must be less than 5MB'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    student_profile.resume = resume_file
    student_profile.save()
    
    return Response({
        'message': 'Resume uploaded successfully',
        'resume_url': student_profile.resume.url if student_profile.resume else None
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_profile_picture(request):
    """Upload profile picture for authenticated user"""
    
    if 'avatar' not in request.FILES:
        return Response({'error': 'No profile picture file provided'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    avatar_file = request.FILES['avatar']
    
    # Validate file type (images only)
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if avatar_file.content_type not in allowed_types:
        return Response({'error': 'Only image files (JPEG, PNG, GIF, WebP) are allowed'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (2MB max)
    if avatar_file.size > 2 * 1024 * 1024:
        return Response({'error': 'File size must be less than 2MB'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Save the avatar to the user model
    request.user.avatar = avatar_file
    request.user.save()
    
    return Response({
        'message': 'Profile picture uploaded successfully',
        'avatar_url': request.user.avatar.url if request.user.avatar else None
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_application_stats(request):
    """Get application statistics for student"""
    try:
        from apps.applications.models import Application
        
        student_profile = get_or_create_student_profile(request.user)[0]
        
        # Get all applications for this student
        applications = Application.objects.filter(student=student_profile)
        
        # Calculate stats
        stats = {
            'total': applications.count(),
            'pending': applications.filter(status='pending').count(),
            'under_review': applications.filter(status='under_review').count(),
            'interview_scheduled': applications.filter(status='interview_scheduled').count(),
            'accepted': applications.filter(status='accepted').count(),
            'rejected': applications.filter(status='rejected').count(),
            'withdrawn': applications.filter(status='withdrawn').count(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get application stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Public Opportuni Card (read-only, no auth)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_opportuni_card(request, student_id):
    """Return a public, shareable snapshot of a student's profile (respecting privacy)."""
    try:
        profile = get_object_or_404(StudentProfile, student_id=student_id)
        user = profile.user
        # Basic identity
        data = {
            'student_id': profile.student_id,
            'name': user.get_full_name() or user.email,
            'avatar_url': getattr(user, 'avatar', None).url if getattr(user, 'avatar', None) else None,
            'university': profile.university,
            'major': profile.major,
            'location': profile.location,
            'bio': profile.bio,
            'portfolio_url': profile.portfolio_url,
        }
        # Respect visibility prefs
        if profile.email_visible:
            data['email'] = user.email
        if profile.phone_visible and profile.phone:
            data['phone'] = profile.phone

        # Recent education (most recent first via model Meta ordering)
        edu = profile.education.all().order_by('-start_date')[:1]
        data['education'] = [
            {
                'institution': e.institution,
                'degree': e.degree,
                'field_of_study': e.field_of_study,
                'start_date': e.start_date.isoformat(),
                'end_date': e.end_date.isoformat() if e.end_date else None,
                'gpa': float(e.gpa) if e.gpa is not None else None,
            } for e in edu
        ]

        # Top 6 skills by proficiency, fallback to name asc
        skills_qs = profile.skills.select_related('skill').all()
        skills_sorted = sorted(
            skills_qs,
            key=lambda s: (-(s.proficiency_level or 0), (s.skill.name or '').lower())
        )[:6]
        data['skills'] = [
            {
                'name': s.skill.name,
                'category': s.skill.category,
                'proficiency_level': s.proficiency_level,
            } for s in skills_sorted
        ]

        # Featured or latest project
        proj = (
            profile.projects.filter(featured=True).order_by('-start_date').first()
            or profile.projects.order_by('-start_date').first()
        )
        if proj:
            data['project'] = {
                'title': proj.title,
                'description': proj.description,
                'project_url': proj.project_url,
                'github_url': proj.github_url,
                'start_date': proj.start_date.isoformat(),
                'end_date': proj.end_date.isoformat() if proj.end_date else None,
                'is_ongoing': proj.is_ongoing,
            }

        # Latest experience
        exp = profile.experiences.order_by('-start_date').first()
        if exp:
            data['experience'] = {
                'title': exp.title,
                'company': exp.company,
                'experience_type': exp.experience_type,
                'location': exp.location,
                'start_date': exp.start_date.isoformat(),
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'is_current': exp.is_current,
            }

        # Recent achievements (top 2)
        ach_qs = profile.achievements.order_by('-date_achieved')[:2]
        data['achievements'] = [
            {
                'title': a.title,
                'achievement_type': a.achievement_type,
                'issuing_organization': a.issuing_organization,
                'date_achieved': a.date_achieved.isoformat(),
                'certificate_url': a.certificate_url,
            } for a in ach_qs
        ]

        # Languages (up to 6)
        lang_qs = profile.languages.all()[:6]
        data['languages'] = [
            {
                'language': l.language,
                'proficiency': l.proficiency,
            } for l in lang_qs
        ]

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Not found or unavailable: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
