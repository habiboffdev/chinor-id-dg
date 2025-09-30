from rest_framework import generics, status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.conf import settings
import hashlib
import hmac
import time
from urllib.parse import parse_qsl
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    ProfileSerializer, 
    ChangePasswordSerializer,
    LogoutResponseSerializer,
    TelegramAuthSerializer,
    TelegramAuthResponseSerializer,
    TelegramConfigSerializer
)
from .models import Profile

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user_data = UserSerializer(user).data
            response.data['user'] = user_data
        return response

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password.']}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password updated successfully'}, 
                          status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    operation_id="accounts_logout",
    summary="Logout User",
    description="Logout the authenticated user (client should delete the token)",
    responses={
        200: LogoutResponseSerializer,
        401: OpenApiResponse(description="Authentication required"),
    },
    tags=["accounts"],
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout view - client should delete the token
    """
    return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)


def verify_telegram_auth(auth_data):
    """
    Verify that the auth data received from Telegram is authentic.
    """
    check_hash = auth_data.pop('hash', None)
    if not check_hash:
        return False
    
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not bot_token:
        return False
    
    # Create a data string
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        data_check_arr.append(f'{key}={value}')
    data_check_string = '\n'.join(data_check_arr)
    
    # Create secret key
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Calculate hash
    hash_check = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # Check if the hash matches
    if hash_check != check_hash:
        return False
    
    # Check if auth data is not too old (5 minutes)
    auth_date = int(auth_data.get('auth_date', 0))
    if time.time() - auth_date > 300:  # 5 minutes
        return False
    
    return True


@extend_schema(
    operation_id="accounts_telegram_auth",
    summary="Telegram Authentication",
    description="Authenticate user with Telegram login data",
    request=TelegramAuthSerializer,
    responses={
        200: TelegramAuthResponseSerializer,
        400: OpenApiResponse(description="Invalid Telegram authentication data"),
        500: OpenApiResponse(description="Authentication failed"),
    },
    tags=["accounts"],
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def telegram_auth(request):
    """
    Authenticate user with Telegram login data
    """
    try:
        # Get Telegram login data from request
        telegram_data = request.data
        
        # Verify the Telegram data integrity
        if not verify_telegram_auth(telegram_data):
            return Response(
                {'error': 'Invalid Telegram authentication data'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        telegram_id = telegram_data.get('id')
        username = telegram_data.get('username', '')
        first_name = telegram_data.get('first_name', '')
        last_name = telegram_data.get('last_name', '')
        
        # Try to find existing user by telegram_id
        try:
            user = User.objects.get(telegram_id=telegram_id)
            # Update user info if needed
            if username and not user.username.startswith('tg_'):
                user.username = username
                user.save()
        except User.DoesNotExist:
            # Create new user
            username_base = username or f"tg_{telegram_id}"
            # Ensure unique username
            counter = 1
            unique_username = username_base
            while User.objects.filter(username=unique_username).exists():
                unique_username = f"{username_base}_{counter}"
                counter += 1
            
            # Create a placeholder email for Telegram users
            email = f"tg_{telegram_id}@telegram.local"
            
            user = User.objects.create_user(
                username=unique_username,
                email=email,
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                user_type='student',  # Default to student for Telegram users
                is_active=True
            )
            
            # Create StudentProfile for student users
            if user.user_type == 'student':
                from apps.students.models import StudentProfile
                StudentProfile.objects.get_or_create(user=user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Authentication failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="accounts_telegram_config",
    summary="Get Telegram Configuration",
    description="Get Telegram bot configuration for frontend",
    responses={
        200: TelegramConfigSerializer,
    },
    tags=["accounts"],
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def telegram_config(request):
    """
    Get Telegram bot configuration for frontend
    """
    from django.conf import settings
    
    return Response({
        'bot_username': getattr(settings, 'TELEGRAM_BOT_USERNAME', None)
    })
