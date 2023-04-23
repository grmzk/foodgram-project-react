import shutil
import tempfile

from rest_framework import status
from rest_framework.test import APITestCase, override_settings

from recipes.models import Ingredient, Recipe, Tag
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


class RecipesGETTests(APITestCase):
    fixtures = FIXTURES

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


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesPOSTTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'
    RECIPE_DATA = {
        'name': 'recipe1',
        'text': 'some text',
        'tags': [1, 3],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAA'
                 'BieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw'
                 '4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
        'ingredients': [
            {
                'id': 1,
                'amount': 5,
            },
            {
                'id': 8,
                'amount': 7,
            },
        ],
        'cooking_time': 5,
    }
    RECIPES_FIELDS_MAX_LENGTH = {
        'name': 200,
    }
    RECIPES_REQUIRED_FIELDS = RECIPE_DATA.keys()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_adding_recipe(self):
        user = User.objects.get(id=3)
        self.client.force_authenticate(user)
        response = self.client.post(self.URL, data=self.RECIPE_DATA)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg=response.data)
        try:
            recipe = Recipe.objects.get(name=self.RECIPE_DATA['name'])
            recipe.delete()
        except Exception as error:
            self.fail('Adding recipe is not working properly!\n'
                      'Error when getting a new recipe from the database: '
                      f'{error}')

    def test_registration_missing_required_field(self):
        for field in self.RECIPES_REQUIRED_FIELDS:
            with self.subTest(field=field):
                data = self.RECIPE_DATA.copy()
                del_field = field
                del data[del_field]
                response = self.client.post(self.URL, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [del_field])

    def test_non_exists_tag_status_code(self):
        user = User.objects.get(id=3)
        self.client.force_authenticate(user)
        true_id = self.RECIPE_DATA['tags'][0]
        self.RECIPE_DATA['tags'][0] = Tag.objects.latest('id').id + 1
        response = self.client.post(self.URL, data=self.RECIPE_DATA)
        self.RECIPE_DATA['tags'][0] = true_id
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_exists_ingredient_status_code(self):
        user = User.objects.get(id=3)
        self.client.force_authenticate(user)
        true_id = self.RECIPE_DATA['ingredients'][0]['id']
        self.RECIPE_DATA['ingredients'][0]['id'] = (
            Ingredient.objects.latest('id').id + 1
        )
        response = self.client.post(self.URL, data=self.RECIPE_DATA)
        self.RECIPE_DATA['ingredients'][0]['id'] = true_id
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_registration_fields_length_error(self):
        for field, max_length in self.RECIPES_FIELDS_MAX_LENGTH.items():
            with self.subTest(field=field):
                data = self.RECIPE_DATA.copy()
                data[field] = 'a' * (max_length + 1)
                response = self.client.post(self.URL, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [field])
