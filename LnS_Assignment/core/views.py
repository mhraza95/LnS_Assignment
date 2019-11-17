from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from django.contrib.auth.models import User
import jwt
import json
# Create your views here.

def custom_login_required(function):
    def wrapper(request, *args, **kwargs):
        user=request.user
        #print(user)
        #auth = TokenAuthentication()
        #user, error = auth.authenticate(request)
        
        if not (user.id):
            return Response({'Please login to access'})
        else:
            return function(request, *args, **kwargs)
    return wrapper

class MixinView(View):
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
      
        return context

    @method_decorator(custom_login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(self, *args, **kwargs)


class TokenAuthentication(BaseAuthentication):

    model = None

    def get_model(self):
        return User

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token=="null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        payload = jwt.decode(token, "SECRET_KEY")
        email = payload['email']
        userid = payload['id']
        msg = {'Error': "Token mismatch",'status' :"401"}
        try:
            
            user = User.objects.get(
                email=email,
                id=userid,
                is_active=True
            )
            
            #if not user.token['token'] == token:
                #raise exceptions.AuthenticationFailed(msg)
               
        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            return HttpResponse({'Error': "Token is invalid"}, status="403")
        #except User.DoesNotExist:
            #return Response({'Error': "Internal server error"}, status="500")

        return (user, token)

    def authenticate_header(self, request):
        return 'Token'