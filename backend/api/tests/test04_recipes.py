import shutil
import tempfile

from django.forms.models import model_to_dict
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

    def test_adding_recipe_non_auth(self):
        response = self.client.post(self.URL, data=self.RECIPE_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_adding_recipe_missing_required_field(self):
        user = User.objects.get(id=3)
        self.client.force_authenticate(user)
        for field in self.RECIPES_REQUIRED_FIELDS:
            with self.subTest(field=field):
                data = self.RECIPE_DATA.copy()
                del_field = field
                del data[del_field]
                response = self.client.post(self.URL, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [del_field])
        self.client.logout()

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

    def test_adding_recipe_fields_length_error(self):
        user = User.objects.get(id=3)
        self.client.force_authenticate(user)
        for field, max_length in self.RECIPES_FIELDS_MAX_LENGTH.items():
            with self.subTest(field=field):
                data = self.RECIPE_DATA.copy()
                data[field] = 'a' * (max_length + 1)
                response = self.client.post(self.URL, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [field])
        self.client.logout()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesPATCHTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'
    RECIPES_FIELDS_MAX_LENGTH = RecipesPOSTTests.RECIPES_FIELDS_MAX_LENGTH
    RECIPES_REQUIRED_FIELDS = RecipesPOSTTests.RECIPES_REQUIRED_FIELDS

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.recipe = Recipe.objects.filter(author=cls.user)[0]
        cls.url = f'{cls.URL}{cls.recipe.id}/'
        cls.recipe_changed_data = model_to_dict(
            cls.recipe,
            exclude=['id', 'in_favorite', 'in_shopping_cart']
        )
        tags = list()
        for tag in cls.recipe_changed_data['tags']:
            tags.append(tag.id)
        ingredients = list()
        for ingredient in cls.recipe_changed_data['ingredients']:
            ingredients.append(
                {
                    'id': ingredient.ingredient.id,
                    'amount': ingredient.amount,
                }
            )
        cls.recipe_changed_data['image'] = (
            RecipesPOSTTests.RECIPE_DATA['image']
        )
        cls.recipe_changed_data['tags'] = tags
        cls.recipe_changed_data['ingredients'] = ingredients
        cls.recipe_changed_data['cooking_time'] = cls.recipe.cooking_time + 1

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_change_recipe(self):
        response = self.client.patch(self.url, data=self.recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg=response.data)
        recipe = Recipe.objects.get(id=self.recipe.id)
        self.assertEqual(recipe.cooking_time,
                         self.recipe_changed_data['cooking_time'])
        self.recipe.save()

    def test_change_recipe_non_auth(self):
        self.client.logout()
        response = self.client.patch(self.url, data=self.recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_recipe_non_author(self):
        self.client.logout()
        other_user = User.objects.get(id=1)
        self.client.force_authenticate(other_user)
        response = self.client.patch(self.url, data=self.recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def test_non_exists_recipe_status_code(self):
        recipe_changed_data = self.recipe_changed_data.copy()
        invalid_recipe_id = Recipe.objects.latest('id').id + 1
        response = self.client.patch(f'{self.URL}{invalid_recipe_id}/',
                                     data=recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_exists_tag_status_code(self):
        recipe_changed_data = self.recipe_changed_data.copy()
        recipe_changed_data['tags'][0] = Tag.objects.latest('id').id + 1
        response = self.client.patch(self.url, data=recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_exists_ingredient_status_code(self):
        recipe_changed_data = self.recipe_changed_data.copy()
        recipe_changed_data['ingredients'][0]['id'] = (
            Ingredient.objects.latest('id').id + 1
        )
        response = self.client.patch(self.url, data=recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_ingredient_amount_status_code(self):
        recipe_changed_data = self.recipe_changed_data.copy()
        recipe_changed_data['ingredients'][0]['amount'] = 0
        response = self.client.patch(self.url, data=recipe_changed_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertCountEqual(response.data.keys(), ['ingredients'])

    def test_change_recipe_fields_length_error(self):
        for field, max_length in self.RECIPES_FIELDS_MAX_LENGTH.items():
            with self.subTest(field=field):
                data = self.recipe_changed_data.copy()
                data[field] = 'a' * (max_length + 1)
                response = self.client.patch(self.url, data=data)
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertCountEqual(response.data.keys(), [field])


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesDELETETests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.other_user = User.objects.get(id=3)
        cls.recipe = Recipe.objects.filter(author=cls.user)[0]
        cls.other_user_recipe = Recipe.objects.filter(author=cls.other_user)[0]
        cls.url = f'{cls.URL}{cls.recipe.id}/'
        cls.other_user_recipe_url = f'{cls.URL}{cls.other_user_recipe.id}/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_delete_recipe(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_delete_recipe_non_auth(self):
        self.client.logout()
        response = self.client.delete(self.other_user_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(
            Recipe.objects.filter(id=self.other_user_recipe.id).exists()
        )

    def test_delete_recipe_non_author(self):
        response = self.client.delete(self.other_user_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Recipe.objects.filter(id=self.other_user_recipe.id).exists()
        )

    def test_delete_recipe_non_exists(self):
        invalid_recipe_id = Recipe.objects.latest('id').id + 1
        response = self.client.delete(f'{self.URL}{invalid_recipe_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesPOSTShoppingCartTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.sc_recipe = cls.user.shopping_cart.all()[0]
        cls.non_sc_recipe = None
        for recipe in Recipe.objects.all():
            if recipe not in cls.user.shopping_cart.all():
                cls.non_sc_recipe = recipe
                break
        cls.non_sc_url = f'{cls.URL}{cls.non_sc_recipe.id}/shopping_cart/'
        cls.sc_url = f'{cls.URL}{cls.sc_recipe.id}/shopping_cart/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_add_recipe_to_shopping_cart(self):
        response = self.client.post(self.non_sc_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            self.user.shopping_cart.filter(id=self.non_sc_recipe.id).exists()
        )
        keys = ['id', 'name', 'image', 'cooking_time']
        self.assertCountEqual(response.data.keys(), keys)

    def test_add_exists_recipe_to_shopping_cart(self):
        response = self.client.post(self.sc_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_recipe_to_shopping_cart_non_auth(self):
        self.client.logout()
        response = self.client.post(self.non_sc_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesDELETEShoppingCartTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.sc_recipe = cls.user.shopping_cart.all()[0]
        cls.non_sc_recipe = None
        for recipe in Recipe.objects.all():
            if recipe not in cls.user.shopping_cart.all():
                cls.non_sc_recipe = recipe
                break
        cls.non_sc_url = f'{cls.URL}{cls.non_sc_recipe.id}/shopping_cart/'
        cls.sc_url = f'{cls.URL}{cls.sc_recipe.id}/shopping_cart/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_delete_recipe_from_shopping_cart(self):
        response = self.client.delete(self.sc_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.user.shopping_cart.filter(id=self.sc_recipe.id).exists()
        )

    def test_delete_non_exists_recipe_from_shopping_cart(self):
        response = self.client.delete(self.non_sc_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_recipe_from_shopping_cart_non_auth(self):
        self.client.logout()
        response = self.client.delete(self.sc_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesGETShoppingCartTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.url = f'{cls.URL}download_shopping_cart/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_get_shopping_cart(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_shopping_cart_non_auth(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesPOSTFavoriteTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.favorite_recipe = cls.user.favorite.all()[0]
        cls.non_favorite_recipe = None
        for recipe in Recipe.objects.all():
            if recipe not in cls.user.favorite.all():
                cls.non_favorite_recipe = recipe
                break
        cls.non_favorite_url = (f'{cls.URL}{cls.non_favorite_recipe.id}'
                                '/favorite/')
        cls.favorite_url = f'{cls.URL}{cls.favorite_recipe.id}/favorite/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_add_recipe_to_favorite(self):
        response = self.client.post(self.non_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            self.user.favorite.filter(id=self.non_favorite_recipe.id).exists()
        )
        keys = ['id', 'name', 'image', 'cooking_time']
        self.assertCountEqual(response.data.keys(), keys)

    def test_add_exists_recipe_to_favorite(self):
        response = self.client.post(self.favorite_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_recipe_to_favorite_non_auth(self):
        self.client.logout()
        response = self.client.post(self.non_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipesDELETEFavoriteTests(APITestCase):
    fixtures = FIXTURES

    URL = '/api/recipes/'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(id=2)
        cls.favorite_recipe = cls.user.favorite.all()[0]
        cls.non_favorite_recipe = None
        for recipe in Recipe.objects.all():
            if recipe not in cls.user.favorite.all():
                cls.non_favorite_recipe = recipe
                break
        cls.non_favorite_url = (f'{cls.URL}{cls.non_favorite_recipe.id}'
                                '/favorite/')
        cls.favorite_url = f'{cls.URL}{cls.favorite_recipe.id}/favorite/'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_delete_recipe_from_favorite(self):
        response = self.client.delete(self.favorite_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.user.favorite.filter(id=self.favorite_recipe.id).exists()
        )

    def test_delete_non_exists_recipe_from_favorite(self):
        response = self.client.delete(self.non_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_recipe_from_favorite_non_auth(self):
        self.client.logout()
        response = self.client.delete(self.favorite_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
