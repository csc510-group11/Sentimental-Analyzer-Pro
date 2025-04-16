from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthAppTests(TestCase):
    def test_register_view_get(self):
        """
        Test that the register view renders the registration form on GET request.
        """
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authapp/register.html')
        self.assertContains(response, '<form')

    def test_register_view_post_valid_data(self):
        """
        Test that the register view creates a new user and redirects on valid POST data.
        """
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_view_post_invalid_data(self):
        """
        Test that the register view does not create a user on invalid POST data.
        """
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'Testpassword123',
            'password2': 'Wrongpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authapp/register.html')
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertContains(response, 'error')

    def test_login_view_get(self):
        """
        Test that the login view renders the login form on GET request.
        """
        response = self.client.get(reverse('login')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authapp/login.html')
        self.assertContains(response, '<form')

    def test_login_view_post_valid_data(self):
        """
        Test that the login view authenticates and redirects on valid POST data.
        """
        # Create a user for testing login
        user = User.objects.create_user(username='testuser', password='Testpassword123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Testpassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_login_view_post_invalid_data(self):
        """
        Test that the login view does not authenticate on invalid POST data.
        """
        user = User.objects.create_user(username='testuser', password='Testpassword123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Wrongpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authapp/login.html')
