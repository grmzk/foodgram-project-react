import json
import unittest

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from . import utils


class UsersGetTests(APITestCase):
    URL = '/api/users/'
    USERS_QUANTITY = 10  # Must be greater than 0

    @classmethod
    def setUpTestData(cls):
        cls.users = list()
        for n in range(0, cls.USERS_QUANTITY):
            user = User.objects.create_user(
                username=f'user{n}',
                first_name=f'Name{n}',
                last_name=f'Family{n}',
                email=f'user{n}@fake.fake'
            )
            cls.users.append(user)

    def test_list_status_code(self):
        response_list = self.client.get(self.URL)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)

    def test_list_pagination_exist(self):
        response_list = self.client.get(self.URL)
        keys = ['count', 'next', 'previous', 'results']
        self.assertCountEqual(response_list.data.keys(), keys)

    def test_list_result_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'username', 'email',
                'first_name', 'last_name', 'is_subscribed']
        self.assertCountEqual(response_list.data['results'][0].keys(), keys)

    def test_list_result_items(self):
        response_list = self.client.get(self.URL)
        finding_users = [
            self.users[0],
            self.users[len(self.users) // 2],
            self.users[-1],
        ]
        for finding_user in finding_users:
            with self.subTest(finding_user=finding_user):
                utils.check_result_items(self, response_list,
                                         finding_user, 'username')

    @unittest.skipIf(USERS_QUANTITY == 1, 'Make no sense with '
                                          '<USERS_QUANTITY = 1>')
    def test_list_pagination_query_params(self):
        response1 = self.client.get(f'{self.URL}?limit={self.USERS_QUANTITY}')
        self.assertEqual(len(response1.data['results']), self.USERS_QUANTITY,
                         'Query param <limit> works incorrectly!')
        half_index = self.USERS_QUANTITY // 2
        username1 = response1.data['results'][half_index]['username']
        response2 = self.client.get(f'{self.URL}?page=2&limit={half_index}')
        username2 = response2.data['results'][0]['username']
        self.assertEqual(username1, username2, 'Query params <page> and '
                                               '<limit> works incorrectly!')

    def test_detail_status_code(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_status_code_non_exists(self):
        user_id = self.USERS_QUANTITY + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_result_keys(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        keys = ['id', 'username', 'email',
                'first_name', 'last_name', 'is_subscribed']
        self.assertCountEqual(response.data.keys(), keys)

    def test_detail_result_values(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        user = User.objects.get(id=user_id)
        keys = ['id', 'username', 'email',
                'first_name', 'last_name']
        user_dict = dict()
        for key in keys:
            user_dict[key] = getattr(user, key)
        user_dict['is_subscribed'] = False
        self.assertDictEqual(json.loads(response.content), user_dict)
