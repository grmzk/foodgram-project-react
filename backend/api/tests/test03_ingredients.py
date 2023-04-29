import json

from rest_framework import status
from rest_framework.test import APITestCase

from recipes.models import Ingredient, MeasurementUnit


class IngredientsTests(APITestCase):
    URL = '/api/ingredients/'
    INGREDS_QUANTITY = 10  # Must be greater than 0

    @classmethod
    def setUpTestData(cls):
        cls.unit = MeasurementUnit.objects.create(name='kn')
        cls.ingreds = list()
        for n in range(0, cls.INGREDS_QUANTITY):
            ingred = Ingredient.objects.create(
                name=f'ingred{n}',
                measurement_unit=cls.unit,
            )
            cls.ingreds.append(ingred)

    def test_list_status_code(self):
        response_list = self.client.get(self.URL)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)

    def test_list_result_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'name', 'measurement_unit']
        self.assertCountEqual(response_list.data[0].keys(), keys)

    def test_list_result_items(self):
        response = self.client.get(self.URL)
        finding_ingreds = [
            self.ingreds[0],
            self.ingreds[len(self.ingreds) // 2],
            self.ingreds[-1],
        ]
        for finding_ingred in finding_ingreds:
            with self.subTest(finding_ingred=finding_ingred):
                results = response.data
                field_name = 'name'
                while True:
                    found = None
                    for item in results:
                        if item[field_name] == getattr(finding_ingred,
                                                       field_name):
                            found = item
                            break
                    if found:
                        break
                    self.fail(f'Item <{finding_ingred}> '
                              'not found in response\'s results!')

    def test_list_query_param(self):
        ingred = Ingredient.objects.create(name='Bacon',
                                           measurement_unit=self.unit)
        key = 'bac'
        response = self.client.get(f'{self.URL}?name={key}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], ingred.name)
        ingred.delete()

    def test_retrieve_result_keys(self):
        ingred_id = self.ingreds[0].id
        response = self.client.get(f'{self.URL}{ingred_id}/')
        keys = ['id', 'name', 'measurement_unit']
        self.assertCountEqual(response.data.keys(), keys)

    def test_retrieve_result_values(self):
        ingred_id = self.ingreds[0].id
        response = self.client.get(f'{self.URL}{ingred_id}/')
        ingred = Ingredient.objects.get(id=ingred_id)
        keys = ['id', 'name']
        ingred_dict = dict()
        for key in keys:
            ingred_dict[key] = getattr(ingred, key)
        ingred_dict['measurement_unit'] = ingred.measurement_unit.name
        self.assertDictEqual(json.loads(response.content), ingred_dict)

    def test_retrieve_non_exists_status_code(self):
        ingred_id = Ingredient.objects.last().id + 1
        response = self.client.get(f'{self.URL}{ingred_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
