import json

from rest_framework import status
from rest_framework.test import APITestCase

from recipes.models import Tag


class TagsTests(APITestCase):
    URL = '/api/tags/'
    TAGS_QUANTITY = 10  # Must be greater than 0

    @classmethod
    def setUpTestData(cls):
        cls.tags = list()
        for n in range(0, cls.TAGS_QUANTITY):
            tag = Tag.objects.create(
                name=f'Tag{n}',
                slug=f'tag{n}',
                color=f'#F{n}',
            )
            cls.tags.append(tag)

    def test_list_status_code(self):
        response_list = self.client.get(self.URL)
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)

    def test_list_result_keys(self):
        response_list = self.client.get(self.URL)
        keys = ['id', 'name', 'slug', 'color']
        self.assertCountEqual(response_list.data[0].keys(), keys)

    def test_list_result_items(self):
        response = self.client.get(self.URL)
        finding_tags = [
            self.tags[0],
            self.tags[len(self.tags) // 2],
            self.tags[-1],
        ]
        for finding_tag in finding_tags:
            with self.subTest(finding_tag=finding_tag):
                results = response.data
                field_name = 'slug'
                while True:
                    found = None
                    for item in results:
                        if item[field_name] == getattr(finding_tag,
                                                       field_name):
                            found = item
                            break
                    if found:
                        break
                    self.fail(f'Item <{finding_tag}> '
                              'not found in response\'s results!')

    def test_retrieve_result_keys(self):
        tag_id = self.tags[0].id
        response = self.client.get(f'{self.URL}{tag_id}/')
        keys = ['id', 'name', 'slug', 'color']
        self.assertCountEqual(response.data.keys(), keys)

    def test_retrieve_result_values(self):
        tag_id = self.tags[0].id
        response = self.client.get(f'{self.URL}{tag_id}/')
        tag = Tag.objects.get(id=tag_id)
        keys = ['id', 'name', 'slug', 'color']
        tag_dict = dict()
        for key in keys:
            tag_dict[key] = getattr(tag, key)
        self.assertDictEqual(json.loads(response.content), tag_dict)

    def test_retrieve_non_exists_status_code(self):
        tag_id = self.TAGS_QUANTITY + 1
        response = self.client.get(f'{self.URL}{tag_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
