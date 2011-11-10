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

        # cache categories data from db in dict
        self.__cat_cache = {}

    @adisp.async
    @adisp.process
    def add_category(self, category, callback):
        redis_result = yield self.client.async.sadd(self.CATEGORIES_KEY,
            category)
        self.__flush_cat_cache()
        callback(category)

    def __flush_cat_cache(self):
        self.__cat_cache.clear()

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
    def flush_words_count_cache(self, category, callback):
        words_cnt_cat_key = self.CATEGORY_WORDS_COUNT_PREFIX % category
        yield self.client.async.delete(words_cnt_cat_key)
        callback(category)

    @adisp.async
    @adisp.process
    def remove_category(self, category, callback=None):
        self.client.async.srem(self.CATEGORIES_KEY, category.lower())
        self.__flush_cat_cache()
        callback(category)

    @adisp.async
    @adisp.process
    def add_words_to_category(self, category, words, callback=None):
        category = category.lower()
        category_key = self.__redis_category_key(category)
        for word, count in words.items():
            yield self.client.async.hincrby(category_key, word, count)
        self.__flush_cat_cache()
        callback(category)

    @adisp.async
    @adisp.process
    def get_categories(self, callback=None):
        categories = {}
        if self.__cat_cache:
            categories_names = self.__cat_cache.keys()
        else:
            categories_names = yield self.client.async.smembers(self.CATEGORIES_KEY)
        for name in categories_names:
            if self.__cat_cache:
                category_words = self.__cat_cache.get(name)
            else:
                category_words = yield self.client.async.hgetall(
                    self.__redis_category_key(name))
                self.__cat_cache[name] = category_words
            category_words_enc = {}
            for word, count in category_words.items():
                category_words_enc[word.decode('UTF-8')] = count
            categories[name] = category_words_enc
        callback(categories.items())

    def __redis_category_key(self, category):
        return self.CATEGORY_KEY_PREFIX % category
