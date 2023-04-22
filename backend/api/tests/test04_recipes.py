import json
import unittest

from rest_framework import status
from rest_framework.test import APITestCase

from recipes.models import Recipe


class RecipesGETTests(APITestCase):
    TEST_FIXTURES_DIR = 'api/tests/fixtures'
    fixtures = [
        f'{TEST_FIXTURES_DIR}/test_user.json',
        f'{TEST_FIXTURES_DIR}/test_subscription.json',
        f'{TEST_FIXTURES_DIR}/test_measurement_unit.json',
        f'{TEST_FIXTURES_DIR}/test_ingredient.json',
        f'{TEST_FIXTURES_DIR}/test_ingredient_amount.json',
        f'{TEST_FIXTURES_DIR}/test_tag.json',
        f'{TEST_FIXTURES_DIR}/test_recipe.json',
    ]

    URL = '/api/recipes/'

    def test_list_status_code(self):
        response_list = self.client.get(self.URL)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)

    def test_list_pagination_exist(self):
        response_list = self.client.get(self.URL)
        keys = ['count', 'next', 'previous', 'results']
        self.assertCountEqual(response_list.data.keys(), keys)

    def test_list_result_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'author', 'tags', 'name',
                'text', 'image', 'ingredients',
                'cooking_time', 'is_favorited', 'is_in_shopping_cart']
        self.assertCountEqual(response_list.data['results'][0].keys(), keys)

    def test_list_result_items(self):
        response = self.client.get(self.URL)
        finding_recipes = [
            Recipe.objects.get(id=1),
            Recipe.objects.get(id=3),
            Recipe.objects.get(id=4),
        ]
        for finding_recipe in finding_recipes:
            with self.subTest(finding_recipe=finding_recipe):
                results = response.data['results']
                field_name = 'name'
                while True:
                    found = None
                    for item in results:
                        if item[field_name] == getattr(finding_recipe,
                                                       field_name):
                            found = item
                            break
                    if found:
                        break
                    if response.data['next']:
                        response = self.client.get(response.data['next'])
                        results = response.data['results']
                        continue
                    self.fail(f'Item <{finding_recipe}> '
                              'not found in response\'s results!')

    # @unittest.skipIf(USERS_QUANTITY == 1, 'Make no sense with '
    #                                       '<USERS_QUANTITY = 1>')
    # def test_list_pagination_query_params(self):
    #     response1 = self.client.get(f'{self.URL}?limit={self.USERS_QUANTITY}')
    #     self.assertEqual(len(response1.data['results']), self.USERS_QUANTITY,
    #                      'Query param <limit> works incorrectly!')
    #     half_index = self.USERS_QUANTITY // 2
    #     username1 = response1.data['results'][half_index]['username']
    #     response2 = self.client.get(f'{self.URL}?page=2&limit={half_index}')
    #     username2 = response2.data['results'][0]['username']
    #     self.assertEqual(username1, username2, 'Query params <page> and '
    #                                            '<limit> works incorrectly!')
    #
    # def test_retrieve_non_auth_status_code(self):
    #     user_id = self.USERS_QUANTITY // 2 + 1
    #     response = self.client.get(f'{self.URL}{user_id}/')
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    # def test_retrieve_non_exists_status_code(self):
    #     user_id = self.USERS_QUANTITY + 1
    #     response = self.client.get(f'{self.URL}{user_id}/')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #
    # def test_retrieve_result_keys(self):
    #     user = self.users[0]
    #     self.client.force_authenticate(user)
    #     user_id = self.USERS_QUANTITY // 2 + 1
    #     response = self.client.get(f'{self.URL}{user_id}/')
    #     keys = ['id', 'username', 'email',
    #             'first_name', 'last_name', 'is_subscribed']
    #     self.assertCountEqual(response.data.keys(), keys)
    #     self.client.logout()
    #
    # def test_retrieve_result_values(self):
    #     user = self.users[0]
    #     self.client.force_authenticate(user)
    #     user_id = self.USERS_QUANTITY // 2 + 1
    #     response = self.client.get(f'{self.URL}{user_id}/')
    #     user = User.objects.get(id=user_id)
    #     keys = ['id', 'username', 'email',
    #             'first_name', 'last_name']
    #     user_dict = dict()
    #     for key in keys:
    #         user_dict[key] = getattr(user, key)
    #     user_dict['is_subscribed'] = False
    #     self.assertDictEqual(json.loads(response.content), user_dict)
    #     self.client.logout()
    #
    # def test_me_non_auth_status_code(self):
    #     response = self.client.get(f'{self.URL}me/')
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    # def test_me_status_code(self):
    #     user_id = self.USERS_QUANTITY // 2 + 1
    #     user = self.users[user_id]
    #     self.client.force_authenticate(user)
    #     response = self.client.get(f'{self.URL}me/')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.client.logout()
    #
    # def test_me_result_keys(self):
    #     user_id = self.USERS_QUANTITY // 2 + 1
    #     user = self.users[user_id]
    #     self.client.force_authenticate(user)
    #     response = self.client.get(f'{self.URL}me/')
    #     keys = ['id', 'username', 'email',
    #             'first_name', 'last_name', 'is_subscribed']
    #     self.assertCountEqual(response.data.keys(), keys)
    #     self.client.logout()
    #
    # def test_me_result_values(self):
    #     user_id = self.USERS_QUANTITY // 2 + 1
    #     user = self.users[user_id]
    #     self.client.force_authenticate(user)
    #     response = self.client.get(f'{self.URL}me/')
    #     keys = ['id', 'username', 'email',
    #             'first_name', 'last_name']
    #     user_dict = dict()
    #     for key in keys:
    #         user_dict[key] = getattr(user, key)
    #     user_dict['is_subscribed'] = False
    #     self.assertDictEqual(json.loads(response.content), user_dict)
    #     self.client.logout()
