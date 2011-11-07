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
    CATEGORY_WORDS_COUNT_PREFIX = 'bayes:category:%s:words:cnt'
    CATEGORIES_KEY = 'bayes:categories'

    def __init__(self, redis_host, redis_port):
        self.client = Client(redis_host, redis_port)
        self.client.connect()

    @adisp.async
    @adisp.process
    def add_category(self, category, callback):
        redis_result = yield self.client.async.sadd(self.CATEGORIES_KEY,
            category)
        callback(category)

    @adisp.async
    @adisp.process
    def words_count_in_cat(self, category, words, callback):
        """Return number of words in  category
        """
        db_key = self.CATEGORY_WORDS_COUNT_PREFIX % category
        words_count_db = yield self.client.async.get(db_key)
        if words_count_db is not None:
            words_count = int(words_count_db)
        else:
            words_count = sum(map(int, words.values()))
            yield self.client.async.set(db_key, words_count)
        callback(words_count)

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
            category_words = yield self.client.async.hgetall(
                self.__redis_category_key(name))
            category_words_enc = {}
            for word, count in category_words.items():
                category_words_enc[word.decode('UTF-8')] = count
            categories[name] = category_words_enc
        callback(categories.items())

    def __redis_category_key(self, category):
        return self.CATEGORY_KEY_PREFIX % category
