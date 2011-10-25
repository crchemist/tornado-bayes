from abc import ABCMeta
from functools import partial

from brukva import Client

class Storage(object):
    """Abstract class for storages.
    """
    __metaclass__ = ABCMeta


class MemoryStorage(Storage):
    """Store train results in python dict.
    """

    def __init__(self):
        self.categories = {}

    def add_category(self, category):
        self.categories.setdefault(category.lower(), {})

    def remove_category(self, category):
        del self.categories[category.lower()]

    def add_word_to_category(self, category, word, count):
        category = category.lower()
        self.categories[category][word] = self.categories[category].get(word,
            0) + count

    def get_categories(self):
        return self.categories.items()


class RedisStorage(Storage):
    """Store train results in redis database.
    """
    CATEGORY_KEY_PREFIX = 'bayes:category:%s'
    CATEGORIES_KEY = 'bayes:categories'

    def __init__(self, redis_host, redis_port):
        self.client = Client(redis_host, redis_port)
        self.client.connect()

    def add_category(self, category, callback=None):
        on_category_added = partial(self.__on_redis_action, callback)
        self.client.sadd(self.CATEGORIES_KEY, category.lower(),
            on_category_added)

    def remove_category(self, category, callback=None):
        on_category_removed = partial(self.__on_redis_action, callback)
        self.client.srem(self.CATEGORIES_KEY, category.lower(),
            on_category_removed)

    def add_word_to_category(self, category, word, count, callback=None):
        category = category.lower()
        category_key = self.__redis_category_key(category)
        on_added_word = partial(self.__on_redis_action, callback)
        self.client.hincrby(category_key, word, count, on_added_word)

#    def get_categories(self, callback=None):
#        self.client.


    def __on_redis_action(self, callback=None, redis_result=None):
        if callback is not None:
            callback(redis_result)

    def __redis_category_key(self, category):
        return self.CATEGORY_KEY_PREFIX % category
