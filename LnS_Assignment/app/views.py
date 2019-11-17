import jwt
import json
from django.contrib.auth.models import User
from rest_framework import status, exceptions 
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,  get_authorization_header
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import authentication
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist

from core.views import MixinView
from .models import Contact, UserContactMapping, UserProfile
from .serializers import UserSerializer, ContactWithLoginSerializer, ContactWithoutLoginSerializer, UserContactMappingSerializer, UserProfileSerializer

# Create your views here.
'''
View class to get contact list and add new contact lists
Http GET and POST operations only
GET operation: returns list of users detail without email, Provided user not logged in
               returns list of users detail with email, Provided user logged in
POST operation: Add new contact to record, Provided user logged in
'''
class ContactList(APIView):

    def get(self, request):

        auth = TokenAuthentication()
        user, error = auth.authenticate(request)
        if error:
            contacts = Contact.objects.all()
            serializers = ContactWithoutLoginSerializer(contacts, many=True)
            print(serializers.data)
            return Response(serializers.data)
        else:
            contacts = Contact.objects.all()
            serializers = ContactWithLoginSerializer(contacts, many=True)
            print(serializers.data)
            return Response(serializers.data)

    def post(self, request):

        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            if error:
                return Response({'Please login to access'})
            else:
                name = request.data.get('name', None)
                email = request.data.get('email', None)
                phone = request.data.get('phone', None)
                contact = Contact(
                    name=name,
                    phone=phone,
                    email=email
                )
                contact.save()

                # mapping the contact to the user who saved it
                mapped = UserContactMapping(
                    user=user,
                    contact=contact
                ).save()

                response = {
                    'msg': 'Contact saved successfully',
                    'data': request.data
                }
                return Response(
                    response,
                    status=200,
                    content_type="application/json"
                )
        except expression as identifier:
            return HttpResponse(
                json.dumps({'Error': "Internal server error"}),
                status=500,
                content_type="application/json"
            )
        


'''
View class to create account
Http POST operations only
Return Success message, Provided contact number not already registered
'''
class SignupList(APIView):

    def post(self, request, *args, **kwargs):

        print(request.data)
        if not request.data:

            return Response({"Error": "Please provide all fields"}, status=status.HTTP_204_NO_CONTENT)

        password = request.data.get('password', None)
        email = request.data.get('email', '')
        phone = request.data.get('phone', None)
        name = request.data.get('name', None)

        
        #print(phone_check)

        try:
            
            phone_check = UserProfile.objects.get(phone=phone)
            print(phone_check)
            if phone_check:

                return Response({"Error": "Phone Number Exists"})
        except ObjectDoesNotExist:
            
            try :
                user = User(
                    username=phone,
                    first_name=name,
                    password=password
                )

                user.set_password(password)
                user.save()

                user_profile = UserProfile(
                    user=user,
                    phone=phone
                ).save()
            except:

                return Response({"Error": "Username already exists"})

        
        return Response({'User Created'})

'''
View class to Login
Http POST operations only
Returns JWT Token for Authentication
'''
class LoginList(APIView):

    
    def post(self, request):

        #if not request.data:

            #return Response({"Error": "Please provide username and password"}, status=status.HTTP_204_NO_CONTENT)

        username = request.data.get('phone', None)
        password = request.data.get('password', None)

        print(username)
        if authenticate(username=username, password=password):
                user = User.objects.get(username=username)
                
                payload = {
                    'id': user.id,
                    'username': user.username
                }

                jwt_token = {'token': jwt.encode(payload, 'SECRET_KEY')}
                
        else:
                return Response({"Error": "Invalid login  details"})

            
        return Response(jwt_token)

'''
Utility class for To generate Authentication token using JWT
(JSON Web Token)
'''
class TokenAuthentication(authentication.BaseAuthentication):

    model = None

    def get_model(self):
        return User

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return ('', {'Error': "No token provided"})

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
        username = payload['username']
        userid = payload['id']
        msg = {'Error': "Token mismatch",'status' :"401"}
        try:
            
            user = User.objects.get(
                username=username,
                id=userid,
                is_active=True
            )
            
            #if not user.token['bearer'] == token:
                #raise exceptions.AuthenticationFailed(msg)
               
        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            return ('', {'Error': "Token is invalid"})
        #except User.DoesNotExist:
            #return Response({'Error': "Internal server error"}, status="500")

        return (user, '')

    def authenticate_header(self, request):
        return 'Token'

'''
View class to mark contact spam
Http POST operation only
Returns Success Message
'''
class SpamList(APIView):
    def post(self, request):
        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            print(error)
            if (error):
                #print('errrr')
                return Response(
                    error,
                    status.HTTP_404_NOT_FOUND
                )
            else:
                phone = request.data.get('phone', None)
                a = Contact.objects.filter(phone=phone).update(spam=True)
                b = UserProfile.objects.filter(phone=phone).update(spam=True)

                print(a)
                if (a + b):
                    return Response(
                        {'message': "Contact marked as spam"},
                        status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'message': "Contact does not exist"},
                        status.HTTP_404_NOT_FOUND
                    )

        except:
            return Response(
                {'Error': status.HTTP_500_INTERNAL_SERVER_ERROR},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

'''
View class to search user details by name
Http POST operations only
Return Users detail by name
'''
class SearchNameList(APIView):
    def get(self, request):
        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            if (error):
                return Response(
                    error,
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                name = request.query_params.get('name', None)

                a = Contact.objects.all().filter(name=name)
                b = Contact.objects.all().filter(name__contains=name).exclude(name=name).order_by('name')
                print(a)
                print(b)
                
                if not a.exists() and  not b.exists():

                    response = {'Error': status.HTTP_404_NOT_FOUND}
                
                else:
                    response = []
                    for contact in a:
                        response.append({
                            'name': contact.name,
                            'phone': contact.phone,
                            'spam': contact.spam
                        })
                    for contact in b:
                        response.append({
                            'name': contact.name,
                            'phone': contact.phone,
                            'spam': contact.spam
                        })

                return Response(
                    response,
                    status.HTTP_200_OK
                )
        except:
            return  Response(
                {'Error': status.HTTP_500_INTERNAL_SERVER_ERROR},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

'''
View class to search user details by contact number
Http POST operations only
Returns users detail by  number
'''
class SearchPhoneList(APIView):
    def get(self, request):
        phone = request.query_params.get('phone', None)

        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            if (error):
                return Response(
                    error,
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                profile = UserProfile.objects.get(phone=phone)
                print(profile.id)
                if (profile):
                    user = User.objects.get(
                        id=profile.id,
                        is_active=True
                    )
                    print(user)
                response = {
                    'name': user.username,
                    'phone': profile.phone,
                    'spam': profile.spam,
                    'email': user.email
                }

                return Response(
                    response,
                    status.HTTP_200_OK
                )

        except UserProfile.DoesNotExist:
            contacts = Contact.objects.all().filter(phone__contains=phone)
            print(contacts)
            if contacts.exists():

                response = []
                for contact in contacts:
                    response.append({
                        'name': contact.name,
                        'phone': contact.phone,
                        'spam': contact.spam
                    })
            else:
                response = {'Error': status.HTTP_404_NOT_FOUND}

            return Response(
                response,
                status.HTTP_200_OK
            )

        except:
            return Response(
                {'Error': status.HTTP_500_INTERNAL_SERVER_ERROR},
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )