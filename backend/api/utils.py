from django.db.models import Exists, OuterRef

from users.models import Subscription


def is_subscribed(user_id):
    return Exists(Subscription.objects.filter(author_id=OuterRef('id'),
                                              user_id=user_id))
