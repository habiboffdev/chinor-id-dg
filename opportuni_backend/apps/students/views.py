from rest_framework import generics, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import (
    StudentProfile, Education, Experience, Skill, StudentSkill,
    Project, Achievement, Language, SocialLink,
    AcademicExam, AcademicExamSection, StudentExamScore,
)
from .serializers import (
    StudentProfileSerializer, StudentProfileUpdateSerializer,
    EducationSerializer, ExperienceSerializer, SkillSerializer,
    StudentSkillSerializer, ProjectSerializer, AchievementSerializer,
    LanguageSerializer, SocialLinkSerializer, StudentDashboardSerializer,
    AcademicExamSerializer, AcademicExamSectionSerializer, StudentExamScoreSerializer,
    ProfilePictureUploadSerializer, ProfilePictureResponseSerializer,
    ResumeUploadSerializer, ResumeUploadResponseSerializer,
    StudentApplicationStatsSerializer, PublicOpportuniCardSerializer,
    SocialLinkUpsertSerializer, DefaultExamsSeedResponseSerializer,
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Education.objects.none()
            
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Education.objects.none()
            
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Education.objects.filter(student=student_profile)

# Experience Views
class ExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return StudentSkill.objects.filter(student=student_profile)

# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Project.objects.filter(student=student_profile)

# Achievement Views
class AchievementListCreateView(generics.ListCreateAPIView):
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Achievement.objects.filter(student=student_profile)

# Language Views
class LanguageListCreateView(generics.ListCreateAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
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
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        student_profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return Language.objects.filter(student=student_profile)

# Social Links Views
class SocialLinkListCreateView(generics.ListCreateAPIView):
    serializer_class = SocialLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        student_profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return SocialLink.objects.filter(student=student_profile)

    def perform_create(self, serializer):
        student_profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        serializer.save(student=student_profile)


class SocialLinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SocialLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        student_profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return SocialLink.objects.filter(student=student_profile)


@extend_schema(
    operation_id="students_upsert_social_link",
    summary="Upsert Social Link",
    description="Create or update a single social link by platform for the current student",
    request=SocialLinkUpsertSerializer,
    responses={
        200: SocialLinkSerializer,
        400: OpenApiResponse(description="Bad request - platform and url are required"),
        401: OpenApiResponse(description="Authentication required"),
    },
    tags=["students"],
)
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
@extend_schema(
    operation_id="student_upload_resume",
    summary="Upload Resume",
    description="Upload a resume file for the authenticated student profile",
    request=ResumeUploadSerializer,
    responses={
        200: ResumeUploadResponseSerializer,
        400: OpenApiResponse(description="Bad request - invalid file type or size"),
        401: OpenApiResponse(description="Authentication required"),
    },
    tags=["students"],
)
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

@extend_schema(
    operation_id="student_upload_profile_picture",
    summary="Upload Profile Picture",
    description="Upload a profile picture for the authenticated user",
    request=ProfilePictureUploadSerializer,
    responses={
        200: ProfilePictureResponseSerializer,
        400: OpenApiResponse(description="Bad request - invalid file type or size"),
        401: OpenApiResponse(description="Authentication required"),
    },
    tags=["students"],
)
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

@extend_schema(
    operation_id="students_get_application_stats",
    summary="Get Student Application Statistics",
    description="Get application statistics for the authenticated student",
    responses={
        200: StudentApplicationStatsSerializer,
        401: OpenApiResponse(description="Authentication required"),
        500: OpenApiResponse(description="Failed to get statistics"),
    },
    tags=["students"],
)
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


# Academic Exams endpoints
class AcademicExamListView(generics.ListAPIView):
    queryset = AcademicExam.objects.all().prefetch_related('sections')
    serializer_class = AcademicExamSerializer
    permission_classes = [permissions.IsAuthenticated]


class AcademicExamSectionListView(generics.ListAPIView):
    serializer_class = AcademicExamSectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        exam_id = self.kwargs.get('exam_id')
        return AcademicExamSection.objects.filter(exam_id=exam_id)


class StudentExamScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentExamScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        profile, _ = get_or_create_student_profile(self.request.user)
        # exam and section are FK (select_related OK); sections is reverse M2O from exam, so prefetch
        return (
            StudentExamScore.objects
            .filter(student=profile)
            .select_related('exam', 'section')
            .prefetch_related('exam__sections')
        )

    def perform_create(self, serializer):
        profile, _ = get_or_create_student_profile(self.request.user)
        serializer.save(student=profile)


class StudentExamScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentExamScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentSkill.objects.none()
        profile, _ = get_or_create_student_profile(self.request.user)
        return StudentExamScore.objects.filter(student=profile)


@extend_schema(
    operation_id="students_seed_default_exams",
    summary="Seed Default Exams",
    description="Seed a set of default exams with common sections (SAT, GRE, IELTS, TOEFL). Safe to call multiple times.",
    request=None,
    responses={
        200: DefaultExamsSeedResponseSerializer,
        401: OpenApiResponse(description="Authentication required"),
        500: OpenApiResponse(description="Failed to seed exams"),
    },
    tags=["students"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def seed_default_exams(request):
    """Seed a set of default exams with common sections.

    This ensures global exam definitions exist (once) so students can add their own
    scores against them. Safe to call multiple times.

    Seeded exams:
    - SAT: Math, English (200–800 step 10)
    - GRE: Verbal, Quantitative (130–170 step 1), Analytical Writing (0–6 step 1)
    - GMAT: Quantitative (6–51 step 1), Verbal (6–51 step 1), IR (1–8 step 1), AWA (0–6 step 1)
    - IELTS: Listening/Reading/Writing/Speaking (0–9 step 1)
    - TOEFL iBT: Reading/Listening/Speaking/Writing (0–30 step 1)
    """
    created = []

    def ensure_exam(slug, name, sections):
        ex, ex_created = AcademicExam.objects.get_or_create(slug=slug, defaults={'name': name})
        if ex_created:
            created.append(name)
        # Create sections if missing
        for idx, s in enumerate(sections, start=1):
            AcademicExamSection.objects.get_or_create(
                exam=ex,
                name=s['name'],
                defaults={
                    'min_score': s.get('min', 0),
                    'max_score': s.get('max', 0),
                    'step': s.get('step', 1),
                    'sort_order': s.get('order', idx),
                }
            )

    # SAT
    ensure_exam('sat', 'SAT', [
        {'name': 'Math', 'min': 200, 'max': 800, 'step': 10, 'order': 1},
        {'name': 'English', 'min': 200, 'max': 800, 'step': 10, 'order': 2},
    ])

    # GRE
    ensure_exam('gre', 'GRE', [
        {'name': 'Verbal Reasoning', 'min': 130, 'max': 170, 'step': 1, 'order': 1},
        {'name': 'Quantitative Reasoning', 'min': 130, 'max': 170, 'step': 1, 'order': 2},
        {'name': 'Analytical Writing', 'min': 0, 'max': 6, 'step': 1, 'order': 3},
    ])

    # GMAT (classic scales simplified to integer steps)
    ensure_exam('gmat', 'GMAT', [
        {'name': 'Quantitative', 'min': 6, 'max': 51, 'step': 1, 'order': 1},
        {'name': 'Verbal', 'min': 6, 'max': 51, 'step': 1, 'order': 2},
        {'name': 'Integrated Reasoning', 'min': 1, 'max': 8, 'step': 1, 'order': 3},
        {'name': 'Analytical Writing Assessment', 'min': 0, 'max': 6, 'step': 1, 'order': 4},
    ])

    # IELTS — typically users share Overall band. Use one Overall section (1.0–9.0, step 0.5)
    ensure_exam('ielts', 'IELTS', [
        {'name': 'Overall', 'min': 1.0, 'max': 9.0, 'step': 0.5, 'order': 1},
    ])

    # TOEFL iBT
    ensure_exam('toefl', 'TOEFL iBT', [
        {'name': 'Reading', 'min': 0, 'max': 30, 'step': 1, 'order': 1},
        {'name': 'Listening', 'min': 0, 'max': 30, 'step': 1, 'order': 2},
        {'name': 'Speaking', 'min': 0, 'max': 30, 'step': 1, 'order': 3},
        {'name': 'Writing', 'min': 0, 'max': 30, 'step': 1, 'order': 4},
    ])

    return Response({'message': 'Defaults ensured', 'created': created}, status=status.HTTP_200_OK)


# Public Opportuni Card (read-only, no auth)
@extend_schema(
    operation_id="students_get_public_opportuni_card",
    summary="Get Public Student Card",
    description="Get a public, shareable snapshot of a student's profile (respecting privacy)",
    responses={
        200: PublicOpportuniCardSerializer,
        404: OpenApiResponse(description="Student profile not found"),
    },
    tags=["students"],
)
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

        # Academic exam scores summary (public): per-exam totals and section details
        try:
            scores = (
                StudentExamScore.objects
                .filter(student=profile)
                .select_related('exam', 'section')
                .order_by('exam__name', 'section__sort_order')
            )
            exams = {}
            for s in scores:
                ex_id = s.exam_id
                if ex_id not in exams:
                    exams[ex_id] = {
                        'exam': s.exam.name,
                        'slug': getattr(s.exam, 'slug', None),
                        'total': 0,
                        'max': 0,
                        'sections': []
                    }
                exams[ex_id]['total'] += int(s.score or 0)
                exams[ex_id]['sections'].append({
                    'name': s.section.name,
                    'score': int(s.score or 0),
                })
            # Compute theoretical max totals per exam from all sections
            for ex_id, rec in exams.items():
                try:
                    exam_obj = AcademicExam.objects.prefetch_related('sections').get(id=ex_id)
                    rec['max'] = sum(int(sec.max_score or 0) for sec in exam_obj.sections.all())
                except AcademicExam.DoesNotExist:
                    rec['max'] = None
            data['exam_scores'] = list(exams.values())
        except Exception:
            data['exam_scores'] = []

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Not found or unavailable: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
