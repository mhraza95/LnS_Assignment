import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Contact, UserContactMapping, UserProfile


class ContactTestCase(TestCase):
    fixtures = ['contact.json']
    
    def setUp(self):
        super().setUp()
        self.contact_1 = Contact.objects.get(pk=1)
        self.contact_2 = Contact.objects.get(pk=2)
    
    def test_marked_spam(self):
        # check for default spam mark
        self.assertFalse(self.contact_1.spam)
        self.assertFalse(self.contact_2.spam)
        
        # Modify & check again.
        self.contact_1.spam = True
        self.contact_1.save()
        self.assertTrue(self.contact_1.spam)
    
    def test_better_defaults(self):
        contact = Contact.objects.create(
            name="Amit Kumar", phone="9000002222"
        )
        self.assertEqual(contact.spam, False)
        self.assertEqual(contact.email, None)


class UserProfileTestCase(TestCase):
    fixtures = ['contact.json']
    
    def test_user_profile(self):
        choice_1 = User.objects.get(id=14)
        choice_2 = UserProfile.objects.get(id=11)
        
        self.assertEqual(User.objects.get(id=14).username, 62007680000)
        self.assertEqual(UserProfile.objects.get(id=11).phone, 62007680000)
        
        choice_1.username
        self.assertEqual(User.objects.get(id=14).username, 62007680000)
        self.assertEqual(UserProfile.objects.get(id=11).phone, 62007680000)
        
        choice_2.phone
        self.assertEqual(User.objects.get(id=14).username, 62007680000)
        self.assertEqual(UserProfile.objects.get(id=211).phone, 62007680000)
        
        choice_1.username
        self.assertEqual(User.objects.get(pk=14).username, 62007680000)
        self.assertEqual(UserProfile.objects.get(pk=11).phone, 62007680000)