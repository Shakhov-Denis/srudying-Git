from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Session, BusinessElement, AccessRule
from .serializers import UserSerializer, AccessRuleSerializer
from .authentication import generate_jwt
from .permissions import has_permission
from django.utils import timezone
from datetime import timedelta

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email, is_active=True)
            if user.check_password(password):
                # Создаём сессию
                session = Session.objects.create(
                    user=user,
                    expires_at=timezone.now() + timedelta(hours=24)
                )
                # Опционально JWT
                jwt_token = generate_jwt(user)
                response = Response({'token': jwt_token, 'session_id': session.session_token})
                response.set_cookie('sessionid', session.session_token, httponly=True)
                return response
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        token = request.COOKIES.get('sessionid')
        if token:
            Session.objects.filter(session_token=token).delete()
        response = Response({'message': 'Logged out'})
        response.delete_cookie('sessionid')
        return response

class ProfileView(APIView):
    def get(self, request):
        if not request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        if not request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        request.user.is_active = False
        request.user.save()
        Session.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Админский API для управления правилами доступа
class AccessRuleListView(APIView):
    def get(self, request):
        if not has_permission(request.user, 'access_rules', 'read'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        rules = AccessRule.objects.all()
        serializer = AccessRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not has_permission(request.user, 'access_rules', 'create'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = AccessRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Mock-ресурсы для демонстрации
class ProductsMockView(APIView):
    def get(self, request):
        if not has_permission(request.user, 'products', 'read'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response({'products': ['product1', 'product2']})

    def post(self, request):
        if not has_permission(request.user, 'products', 'create'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response({'message': 'Product created'}, status=status.HTTP_201_CREATED)

class OrdersMockView(APIView):
    def get(self, request):
        if not has_permission(request.user, 'orders', 'read'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response({'orders': []})