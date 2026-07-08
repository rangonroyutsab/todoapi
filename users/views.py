from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserRegistrationSerializer
from todoapi.utils import format_success_response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return format_success_response(
            data=serializer.data,
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )
