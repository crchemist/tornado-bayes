from abc import ABCMeta
from functools import partial

from tornadotools import adisp

from brukva import Client

class Storage(object):
    """Abstract class for storages.
    """
    __metaclass__ = ABCMeta


class RedisStorage(Storage):
    """Store train results in redis database.
    """
    CATEGORY_KEY_PREFIX = 'bayes:category:%s'
    CATEGORIES_KEY = 'bayes:categories'

    def __init__(self, redis_host, redis_port):
        self.client = Client(redis_host, redis_port)
        self.client.connect()

    @adisp.async
    @adisp.process
    def add_category(self, category, callback):
        redis_result = yield self.client.async.sadd(self.CATEGORIES_KEY, category)
        callback(category)

    @adisp.async
    @adisp.process
    def remove_category(self, category, callback=None):
        self.client.async.srem(self.CATEGORIES_KEY, category.lower())
        callback(category)

    @adisp.async
    @adisp.process
    def add_words_to_category(self, category, words, callback=None):
        category = category.lower()
        category_key = self.__redis_category_key(category)
        for word, count in words.items():
            yield self.client.async.hincrby(category_key, word, count)
        callback(category)

    @adisp.async
    @adisp.process
    def get_categories(self, callback=None):
        categories = {}
        categories_names = yield self.client.async.smembers(self.CATEGORIES_KEY)
        for name in categories_names:
            categories[name] = yield self.client.async.hgetall(
                self.__redis_category_key(name))
        callback(categories.items())

    def __redis_category_key(self, category):
        return self.CATEGORY_KEY_PREFIX % category
