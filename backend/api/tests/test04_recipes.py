from rest_framework import status
from rest_framework.test import APITestCase

from recipes.models import Recipe, Tag
from users.models import User


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

    def test_list_result_author_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'username', 'email',
                'first_name', 'last_name', 'is_subscribed']
        self.assertCountEqual(
            response_list.data['results'][0]['author'].keys(), keys
        )

    def test_list_result_tags_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'name', 'slug', 'color']
        self.assertCountEqual(
            response_list.data['results'][0]['tags'][0].keys(), keys
        )

    def test_list_result_ingredients_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'name', 'measurement_unit', 'amount']
        self.assertCountEqual(
            response_list.data['results'][0]['ingredients'][0].keys(), keys
        )

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

    def test_list_pagination_query_params(self):
        recipes_quantity = Recipe.objects.count()
        response1 = self.client.get(f'{self.URL}?limit={recipes_quantity}')
        self.assertEqual(len(response1.data['results']), recipes_quantity,
                         'Query param <limit> works incorrectly!')
        half_index = recipes_quantity // 2
        recipe_name1 = response1.data['results'][half_index]['name']
        response2 = self.client.get(f'{self.URL}?page=2&limit={half_index}')
        recipe_name2 = response2.data['results'][0]['name']
        self.assertEqual(recipe_name1, recipe_name2,
                         'Query params <page> and <limit> works incorrectly!')

    def test_list_query_params(self):
        user = User.objects.get(id=3)
        self.client.force_authenticate(user)
        user_recipes = list(user.recipes.values_list('name', flat=True))
        response = self.client.get(f'{self.URL}?author={user.id}')
        response_recipes = list()
        for recipe in response.data['results']:
            response_recipes.append(recipe['name'])
        self.assertCountEqual(response_recipes, user_recipes,
                              'Query param <author> works incorrectly!')
        self.client.logout()

        user = User.objects.get(id=2)
        self.client.force_authenticate(user)
        user_recipes = list(user.favorite.values_list('name', flat=True))
        response = self.client.get(f'{self.URL}?is_favorited=1')
        response_recipes = list()
        for recipe in response.data['results']:
            response_recipes.append(recipe['name'])
        self.assertCountEqual(response_recipes, user_recipes,
                              'Query param <is_favorited> works incorrectly!')

        user_recipes = list(user.shopping_cart.values_list('name', flat=True))
        response = self.client.get(f'{self.URL}?is_in_shopping_cart=1')
        response_recipes = list()
        for recipe in response.data['results']:
            response_recipes.append(recipe['name'])
        self.assertCountEqual(response_recipes, user_recipes,
                              'Query param <is_in_shopping_cart> '
                              'works incorrectly!')
        self.client.logout()

        tags = Tag.objects.filter(slug__in=['sour', 'salty']).all()
        tags_recipes = set()
        for tag in tags:
            tags_recipes = tags_recipes.union(
                set(tag.recipes.values_list('name', flat=True))
            )
        response = self.client.get(f'{self.URL}?tags=sour&tags=salty')
        response_recipes = list()
        for recipe in response.data['results']:
            response_recipes.append(recipe['name'])
        self.assertCountEqual(response_recipes, tags_recipes,
                              'Query param <tags> works incorrectly!')

    def test_retrieve_status_code(self):
        recipe_id = 3
        response = self.client.get(f'{self.URL}{recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_exists_status_code(self):
        recipe_id = Recipe.objects.count() + 1
        response = self.client.get(f'{self.URL}{recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_result_keys(self):
        recipe_id = 3
        response = self.client.get(f'{self.URL}{recipe_id}/')
        keys = ['id', 'author', 'tags', 'name',
                'text', 'image', 'ingredients',
                'cooking_time', 'is_favorited', 'is_in_shopping_cart']
        self.assertCountEqual(response.data.keys(), keys)
