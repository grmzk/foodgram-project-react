from django.db import models
from django.http import HttpResponse


def check_result_items(self, response: HttpResponse,
                       finding: models.Model, field_name: str) -> None:
    results = response.data['results']
    while True:
        found = None
        for item in results:
            if item['username'] == getattr(finding, field_name):
                found = item
                break
        if found:
            break
        if response.data['next']:
            response = self.client.get(response.data['next'])
            results = response.data['results']
            continue
        self.fail(f'Item <{finding}> '
                  'not found in response\'s results!')
