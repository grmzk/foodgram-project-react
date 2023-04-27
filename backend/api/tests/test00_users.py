import json
import shutil
import tempfile
import unittest

from rest_framework import status
from rest_framework.test import APITestCase, override_settings

from users.models import User

TEST_FIXTURES_DIR = 'api/tests/fixtures'
FIXTURES = [
    f'{TEST_FIXTURES_DIR}/test_user.json',
    f'{TEST_FIXTURES_DIR}/test_subscription.json',
    f'{TEST_FIXTURES_DIR}/test_measurement_unit.json',
    f'{TEST_FIXTURES_DIR}/test_ingredient.json',
    f'{TEST_FIXTURES_DIR}/test_ingredient_amount.json',
    f'{TEST_FIXTURES_DIR}/test_tag.json',
    f'{TEST_FIXTURES_DIR}/test_recipe.json',
]
MEDIA_ROOT = tempfile.mkdtemp()


class UsersGETTests(APITestCase):
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
                email=f'user{n}@fake.fake',
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
        response = self.client.get(self.URL)
        finding_users = [
            self.users[0],
            self.users[len(self.users) // 2],
            self.users[-1],
        ]
        for finding_user in finding_users:
            with self.subTest(finding_user=finding_user):
                results = response.data['results']
                field_name = 'username'
                while True:
                    found = None
                    for item in results:
                        if item[field_name] == getattr(finding_user,
                                                       field_name):
                            found = item
                            break
                    if found:
                        break
                    if response.data['next']:
                        response = self.client.get(response.data['next'])
                        results = response.data['results']
                        continue
                    self.fail(f'Item <{finding_user}> '
                              'not found in response\'s results!')

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

    def test_retrieve_non_auth_status_code(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_non_exists_status_code(self):
        user_id = self.USERS_QUANTITY + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_result_keys(self):
        user = self.users[0]
        self.client.force_authenticate(user)
        user_id = self.USERS_QUANTITY // 2 + 1
        response = self.client.get(f'{self.URL}{user_id}/')
        keys = ['id', 'username', 'email',
                'first_name', 'last_name', 'is_subscribed']
        self.assertCountEqual(response.data.keys(), keys)
        self.client.logout()

    def test_retrieve_result_values(self):
        user = self.users[0]
        self.client.force_authenticate(user)
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
        self.client.logout()

    def test_me_non_auth_status_code(self):
        response = self.client.get(f'{self.URL}me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_status_code(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        user = self.users[user_id]
        self.client.force_authenticate(user)
        response = self.client.get(f'{self.URL}me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_me_result_keys(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        user = self.users[user_id]
        self.client.force_authenticate(user)
        response = self.client.get(f'{self.URL}me/')
        keys = ['id', 'username', 'email',
                'first_name', 'last_name', 'is_subscribed']
        self.assertCountEqual(response.data.keys(), keys)
        self.client.logout()

    def test_me_result_values(self):
        user_id = self.USERS_QUANTITY // 2 + 1
        user = self.users[user_id]
        self.client.force_authenticate(user)
        response = self.client.get(f'{self.URL}me/')
        keys = ['id', 'username', 'email',
                'first_name', 'last_name']
        user_dict = dict()
        for key in keys:
            user_dict[key] = getattr(user, key)
        user_dict['is_subscribed'] = False
        self.assertDictEqual(json.loads(response.content), user_dict)
        self.client.logout()


class UsersPOSTTests(APITestCase):
    URL = '/api/users/'
    USER_DATA = {
        'username': 'user1',
        'email': 'user1@fake.fake',
        'first_name': 'Name1',
        'last_name': 'Family1',
        'password': 'password1',
    }
    REG_FIELDS_MAX_LENGTH = {
        'username': 150,
        'email': 254,
        'first_name': 150,
        'last_name': 150,
        'password': 150,
    }
    REG_REQUIRED_FIELDS = REG_FIELDS_MAX_LENGTH.keys()

    def test_registration(self):
        response = self.client.post(self.URL, data=self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg=response.data)
        try:
            user = User.objects.get(username=self.USER_DATA['username'])
            user.delete()
        except Exception as error:
            self.fail('Registration is not working properly!\n'
                      'Error when getting a new user from the database: '
                      f'{error}')

    def test_registration_missing_required_field(self):
        for field in self.REG_REQUIRED_FIELDS:
            with self.subTest(field=field):
                data = self.USER_DATA.copy()
                del_field = field
                del data[del_field]
                response = self.client.post(self.URL, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [del_field])

    def test_registration_fields_length_error(self):
        for field, max_length in self.REG_FIELDS_MAX_LENGTH.items():
            with self.subTest(field=field):
                data = self.USER_DATA.copy()
                data[field] = 'a' * (max_length + 1)
                response = self.client.post(self.URL, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [field])

    def test_registration_username_regex_error(self):
        data = self.USER_DATA.copy()
        data['username'] = 'test#1'
        response = self.client.post(self.URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertCountEqual(response.data.keys(), ['username'])

    def test_set_password(self):
        data = {
            'current_password': self.USER_DATA['password'],
            'new_password': 'test_new_password',
        }
        user = User.objects.create_user(**self.USER_DATA)
        self.client.force_authenticate(user)
        response = self.client.post(f'{self.URL}set_password/', data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(user.check_password(data['new_password']))
        user.delete()

    def test_set_password_invalid_password(self):
        data = {
            'current_password': 'invalid_password',
            'new_password': 'test_new_password',
        }
        user = User.objects.create_user(**self.USER_DATA)
        self.client.force_authenticate(user)
        response = self.client.post(f'{self.URL}set_password/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertCountEqual(response.data.keys(), ['current_password'])
        user.delete()

    def test_set_password_missing_required_field(self):
        data = {
            'current_password': self.USER_DATA['password'],
            'new_password': 'test_new_password',
        }
        del_fields = data.keys()
        for del_field in del_fields:
            with self.subTest(del_field=del_field):
                invalid_data = data.copy()
                del invalid_data[del_field]
                user = User.objects.create_user(**self.USER_DATA)
                self.client.force_authenticate(user)
                response = self.client.post(f'{self.URL}set_password/',
                                            data=invalid_data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [del_field])
                user.delete()

    def test_set_password_non_auth_status_code(self):
        data = {
            'current_password': self.USER_DATA['password'],
            'new_password': 'test_new_password',
        }
        response = self.client.post(f'{self.URL}set_password/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UsersGETSubscriptionsTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/users/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.url = f'{cls.URL}subscriptions/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_get_subscriptions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_subscriptions_non_auth(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_subscriptions_pagination_exist(self):
        response_list = self.client.get(self.url)
        keys = ['count', 'next', 'previous', 'results']
        self.assertCountEqual(response_list.data.keys(), keys)

    def test_get_subscriptions_pagination_query_params(self):
        authors_quantity = self.user.follower.all().count()
        response1 = self.client.get(f'{self.url}?limit={authors_quantity}')
        self.assertEqual(len(response1.data['results']), authors_quantity,
                         'Query param <limit> works incorrectly!')
        half_index = authors_quantity // 2
        username1 = response1.data['results'][half_index]['username']
        response2 = self.client.get(f'{self.url}?page=2&limit={half_index}')
        username2 = response2.data['results'][0]['username']
        self.assertEqual(username1, username2, 'Query params <page> and '
                                               '<limit> works incorrectly!')

    def test_get_subscriptions_result_keys(self):
        response_list = self.client.get(self.url)
        keys = ['id', 'username', 'email', 'first_name', 'last_name',
                'is_subscribed', 'recipes', 'recipes_count']
        self.assertCountEqual(response_list.data['results'][0].keys(),
                              keys)

    def test_get_subscriptions_recipes_limit_query_param(self):
        recipes_limit = 1
        response = self.client.get(
            f'{self.url}?recipes_limit={recipes_limit}'
        )
        self.assertLessEqual(len(response.data['results'][0]['recipes']),
                             recipes_limit)

    def test_get_subscriptions_result_recipes_keys(self):
        response_list = self.client.get(self.url)
        keys = ['id', 'name', 'image', 'cooking_time']
        self.assertCountEqual(
            response_list.data['results'][0]['recipes'][0].keys(),
            keys
        )

    def test_get_subscriptions_result_items(self):
        response = self.client.get(self.url)
        results = response.data['results']
        response_authors = list()
        while True:
            for item in results:
                response_authors.append(item['username'])
            if response.data['next']:
                response = self.client.get(response.data['next'])
                results = response.data['results']
                continue
            break
        authors = (User.objects.filter(following__user_id=self.user.id).all()
                   .values_list('username', flat=True))
        self.assertCountEqual(response_authors, authors)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UsersPOSTSubscriptionsTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/users/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.author = (User.objects.filter(following__user_id=cls.user.id)
                      .all()[0])
        cls.non_author = (User.objects.exclude(following__user_id=cls.user.id)
                          .all()[0])
        cls.author_url = f'{cls.URL}{cls.author.id}/subscribe/'
        cls.non_author_url = f'{cls.URL}{cls.non_author.id}/subscribe/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_subscribe(self):
        response = self.client.post(self.non_author_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            self.user.follower.filter(author_id=self.non_author.id).exists(),
            msg='New subscription not found!'
        )
        keys = ['id', 'username', 'email', 'first_name', 'last_name',
                'is_subscribed', 'recipes', 'recipes_count']
        self.assertCountEqual(response.data.keys(), keys)

    def test_subscribe_exists(self):
        response = self.client.post(self.author_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_non_auth(self):
        self.client.logout()
        response = self.client.post(self.non_author_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UsersDELETESubscriptionsTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/users/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.author = (User.objects.filter(following__user_id=cls.user.id)
                      .all()[0])
        cls.non_author = (User.objects.exclude(following__user_id=cls.user.id)
                          .all()[0])
        cls.author_url = f'{cls.URL}{cls.author.id}/subscribe/'
        cls.non_author_url = f'{cls.URL}{cls.non_author.id}/subscribe/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_delete_subscription(self):
        response = self.client.delete(self.author_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.user.follower.filter(author_id=self.author.id).exists(),
            msg='Subscription still exists!'
        )

    def test_delete_non_exists_subscription(self):
        response = self.client.delete(self.non_author_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_subscription_non_auth(self):
        self.client.logout()
        response = self.client.delete(self.author_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
