from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class AuthTokenTests(APITestCase):
    URL = '/api/auth/token/'
    USER_DATA = {
        'username': 'user1',
        'email': 'user1@fake.fake',
        'first_name': 'Name1',
        'last_name': 'Family1',
        'password': 'password1',
    }
    URLS_GET_NEED_TOKEN = [
        '/api/users/1/',
        '/api/users/me/',
    ]
    URLS_POST_NEED_TOKEN = [
        '/api/users/set_password/',
        '/api/auth/token/logout/',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(**cls.USER_DATA)

    def test_login(self):
        data = {
            'email': self.USER_DATA['email'],
            'password': self.USER_DATA['password'],
        }
        response = self.client.post(f'{self.URL}login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCountEqual(response.data.keys(), ['auth_token'])
        auth_token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token}')
        response = self.client.post(f'{self.URL}logout/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(f'{self.URL}logout/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_non_auth(self):
        response = self.client.post(f'{self.URL}logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_urls_need_token(self):
        data = {
            'email': self.USER_DATA['email'],
            'password': self.USER_DATA['password'],
        }
        response = self.client.post(f'{self.URL}login/', data=data)
        auth_token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token}')
        for url in self.URLS_GET_NEED_TOKEN:
            with self.subTest(url=url, msg='Token access is not configured!'):
                response = self.client.get(url)
                self.assertNotEqual(response.status_code,
                                    status.HTTP_401_UNAUTHORIZED)
        for url in self.URLS_POST_NEED_TOKEN:
            with self.subTest(url=url, msg='Token access is not configured!'):
                response = self.client.post(url)
                self.assertNotEqual(response.status_code,
                                    status.HTTP_401_UNAUTHORIZED)
