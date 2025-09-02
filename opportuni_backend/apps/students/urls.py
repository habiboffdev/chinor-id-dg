from django.urls import path
from . import views

urlpatterns = [
    # Student Profile
    path('profile/', views.StudentProfileView.as_view(), name='student-profile'),
    path('dashboard/', views.StudentDashboardView.as_view(), name='student-dashboard'),
    
    # Education
    path('education/', views.EducationListCreateView.as_view(), name='education-list-create'),
    path('education/<int:pk>/', views.EducationDetailView.as_view(), name='education-detail'),
    
    # Experience
    path('experience/', views.ExperienceListCreateView.as_view(), name='experience-list-create'),
    path('experience/<int:pk>/', views.ExperienceDetailView.as_view(), name='experience-detail'),
    
    # Skills
    path('skills/available/', views.SkillListView.as_view(), name='skill-list'),
    path('skills/', views.StudentSkillListCreateView.as_view(), name='student-skill-list-create'),
    path('skills/<int:pk>/', views.StudentSkillDetailView.as_view(), name='student-skill-detail'),
    
    # Projects
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Achievements
    path('achievements/', views.AchievementListCreateView.as_view(), name='achievement-list-create'),
    path('achievements/<int:pk>/', views.AchievementDetailView.as_view(), name='achievement-detail'),
    
    # Languages
    path('languages/', views.LanguageListCreateView.as_view(), name='language-list-create'),
    path('languages/<int:pk>/', views.LanguageDetailView.as_view(), name='language-detail'),

    # Social links
    path('social-links/', views.SocialLinkListCreateView.as_view(), name='social-link-list-create'),
    path('social-links/<int:pk>/', views.SocialLinkDetailView.as_view(), name='social-link-detail'),
    path('social-links/upsert/', views.upsert_social_link, name='social-link-upsert'),
    
    # File Upload
    path('upload-resume/', views.upload_resume, name='upload-resume'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload-profile-picture'),
    
    # Application Stats
    path('application-stats/', views.student_application_stats, name='student-application-stats'),

    # Public Opportuni Card (no auth)
    path('card/<str:student_id>/', views.public_opportuni_card, name='public-opportuni-card'),

    # Academic Exams & Scores
    path('exams/', views.AcademicExamListView.as_view(), name='academic-exam-list'),
    path('exams/<int:exam_id>/sections/', views.AcademicExamSectionListView.as_view(), name='academic-exam-section-list'),
    path('exam-scores/', views.StudentExamScoreListCreateView.as_view(), name='student-exam-score-list-create'),
    path('exam-scores/<int:pk>/', views.StudentExamScoreDetailView.as_view(), name='student-exam-score-detail'),
    path('exams/seed-defaults/', views.seed_default_exams, name='academic-exam-seed-defaults'),
]
