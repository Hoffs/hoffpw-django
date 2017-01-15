from uuid import UUID

from rest_framework import status
from rest_framework.test import APITestCase
from webauth.models import User, AuthToken


# Create your tests here.

class AccountTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new user object.
        """
        url = '/users/'
        data = {'username': 'test_user', 'password': 'test_password', 'email': 'test@email.com'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test_user')

    def test_create_account_length(self):
        """
        Ensure we can't create short usernames.
        """
        url = '/users/'
        data = {'username': 'asd', 'password': 'test_password', 'email': 'test@email.com'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_create_account_duplicate(self):
        """
        Ensure we can't create accounts with same email and username.
        """
        self.test_create_account()
        url = '/users/'
        data = {'username': 'test_user', 'password': 'test_password', 'email': 'test@email.com'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_create_account_duplicate_email(self):
        """
        Ensure we can't create accounts with same email.
        """
        self.test_create_account()
        url = '/users/'
        data = {'username': 'test_user2', 'password': 'test_password', 'email': 'test@email.com'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_create_account_duplicate_username(self):
        """
        Ensure we can't create accounts with same username.
        """
        self.test_create_account()
        url = '/users/'
        data = {'username': 'test_user', 'password': 'test_password', 'email': 'test2@email.com'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_authenticate(self):
        """
        Ensure we can authenticate with the created user.
        """
        self.test_create_account()
        url = '/auth/login/'
        data = {'username': 'test_user', 'password': 'test_password'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['token']
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(AuthToken.objects.count(), 1)
        self.assertEqual(AuthToken.objects.get().key, self.token)
        self.assertEqual(AuthToken.objects.get().user_id, User.objects.get().uuid)

    def test_deauthenticate(self):
        """
        Ensure we can de-authenticate our authorization token.
        """
        self.test_authenticate()
        url = '/auth/logout/'
        data = {}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AuthToken.objects.count(), 1)
        self.assertEqual(AuthToken.objects.get().key, 'logged_out')

    def test_get_users_anonymous(self):
        url = '/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Unauthorized.')

    def test_get_users_authenticated(self):
        self.test_authenticate()
        self.create_dummy_user()
        url = '/users/'
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRaises(KeyError, lambda: response.data['count'])
        self.assertEqual(UUID(response.data['uuid']), AuthToken.objects.get(key=self.token).user_id)

    def test_get_user_uuid(self):
        self.test_create_account()
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], uuid)

    def test_get_user_username(self):
        self.test_create_account()
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], username)

    def test_change_user_uuid_anonymous(self):
        self.create_dummy_user()
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        data = {'username': 'test_user_new'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_email_uuid_anonymous(self):
        self.create_dummy_user()
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        data = {'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_both_uuid_anonymous(self):
        self.create_dummy_user()
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        data = {'username': 'test_user_new', 'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_user_username_anonymous(self):
        self.create_dummy_user()
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        data = {'username': 'test_user_new'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_email_username_anonymous(self):
        self.create_dummy_user()
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        data = {'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_both_username_anonymous(self):
        self.create_dummy_user()
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        data = {'username': 'test_user_new', 'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_user_uuid_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        data = {'username': 'test_user_new'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().username, 'test_user_new')

    def test_change_email_uuid_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        data = {'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().email, 'new_email@email.com')

    def test_change_both_uuid_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/'.format(uuid)
        data = {'username': 'test_user_new', 'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().username, 'test_user_new')
        self.assertEqual(User.objects.get().email, 'new_email@email.com')

    def test_change_user_username_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        data = {'username': 'test_user_new'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().username, 'test_user_new')

    def test_change_email_username_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        data = {'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().email, 'new_email@email.com')

    def test_change_both_username_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        username = str(User.objects.get().username)
        url = '/users/{}/'.format(username)
        data = {'username': 'test_user_new', 'email': 'new_email@email.com'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().username, 'test_user_new')
        self.assertEqual(User.objects.get().email, 'new_email@email.com')

    def test_change_password_uuid_anonymous(self):
        self.test_create_account()
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/change_password/'.format(uuid)
        data = {'old_password': 'test_password', 'new_password1': 'new_password', 'new_password2': 'new_password'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_username_anonymous(self):
        self.test_create_account()
        username = str(User.objects.get().username)
        url = '/users/{}/change_password/'.format(username)
        data = {'old_password': 'test_password', 'new_password1': 'new_password', 'new_password2': 'new_password'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_uuid_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        uuid = str(User.objects.get().uuid)
        url = '/users/{}/change_password/'.format(uuid)
        data = {'old_password': 'test_password', 'new_password1': 'new_password', 'new_password2': 'new_password'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_username_authenticated(self):
        self.test_authenticate()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        username = str(User.objects.get().username)
        url = '/users/{}/change_password/'.format(username)
        data = {'old_password': 'test_password', 'new_password1': 'new_password', 'new_password2': 'new_password'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def create_dummy_user(self, username='dummy', email='dummy@email.com'):
        url = '/users/'
        data = {'username': username, 'email': email, 'password': 'dummy_password'}
        count = User.objects.count()
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(User.objects.count(), count)



