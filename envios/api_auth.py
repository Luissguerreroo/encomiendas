from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


# =========================
# LOGIN CON COOKIES JWT
# =========================

class LoginCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Credenciales inválidas.'},
                status=401
            )

        refresh = RefreshToken.for_user(user)

        response = Response({'message': 'Login exitoso.'})

        # =========================
        # ACCESS TOKEN (COOKIE)
        # =========================
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=False,  # ⚠ en local debe ser False (HTTPS solo en producción)
            samesite='Lax',
            max_age=3600,  # 1 hora
        )

        # =========================
        # REFRESH TOKEN (COOKIE)
        # =========================
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=604800,  # 7 días
        )

        return response


# =========================
# LOGOUT CON COOKIES JWT
# =========================

class LogoutCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({'message': 'Logout exitoso.'})

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response