from django.urls import path
from app import views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Test API')

urlpatterns = [
    path('docs', schema_view),
    path('contact', views.ContactList.as_view()),
    path('signup', views.SignupList.as_view()),
    path('login', views.LoginList.as_view()),
    path('spam', views.SpamList.as_view()),
    path('search_by_name', views.SearchNameList.as_view()),
    path('search_by_phone', views.SearchPhoneList.as_view())
]