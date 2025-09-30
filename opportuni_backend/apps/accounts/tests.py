from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.serializers import UserRegistrationSerializer
from apps.students.models import StudentProfile
from apps.organizations.models import Organization, OrganizationMember

User = get_user_model()


class UserRegistrationSerializerTests(TestCase):
    def setUp(self):
        # Ensure password validators allow this password during tests
        self.password = "Str0ngPass!234"

    def test_creates_student_profile_on_registration(self):
        data = {
            "email": "student@example.com",
            "username": "studentuser",
            "first_name": "Student",
            "last_name": "User",
            "user_type": "student",
            "password": self.password,
            "password_confirm": self.password,
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual(user.user_type, "student")
        self.assertTrue(
            StudentProfile.objects.filter(user=user).exists(),
            "Student profile should be created for student users",
        )

    def test_creates_organization_and_admin_membership(self):
        data = {
            "email": "org@example.com",
            "username": "orguser",
            "first_name": "Org",
            "last_name": "Owner",
            "user_type": "organization",
            "password": self.password,
            "password_confirm": self.password,
            "organization_name": "Example Org",
            "organization_type": "company",
            "organization_description": "We connect students with opportunities.",
            "organization_email": "contact@example.org",
            "organization_country": "Uzbekistan",
            "organization_city": "Tashkent",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        organization = Organization.objects.get(user=user)
        self.assertEqual(organization.name, "Example Org")
        self.assertEqual(organization.organization_type, "company")
        self.assertEqual(organization.country, "Uzbekistan")
        self.assertEqual(organization.city, "Tashkent")
        self.assertEqual(organization.email, "contact@example.org")

        self.assertTrue(
            OrganizationMember.objects.filter(
                organization=organization, user=user, role="admin"
            ).exists(),
            "Organization admin membership should be created for the registering user",
        )

    def test_requires_required_fields_for_organization(self):
        data = {
            "email": "missing@example.com",
            "username": "missingorg",
            "first_name": "Missing",
            "last_name": "Fields",
            "user_type": "organization",
            "password": self.password,
            "password_confirm": self.password,
            # Intentionally omit organization fields
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        for field in [
            "organization_name",
            "organization_type",
            "organization_country",
            "organization_city",
        ]:
            self.assertIn(field, serializer.errors)

    def test_registration_is_atomic_on_organization_failure(self):
        data = {
            "email": "dup@example.com",
            "username": "dupuser",
            "first_name": "Dup",
            "last_name": "User",
            "user_type": "organization",
            "password": self.password,
            "password_confirm": self.password,
            "organization_name": "Dup Org",
            "organization_type": "invalid-type",  # Invalid choice
            "organization_country": "Uzbekistan",
            "organization_city": "Tashkent",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(
            serializer.is_valid()
        )  # Serializer should catch invalid choice via model validation
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Organization.objects.count(), 0)
