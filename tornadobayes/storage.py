from abc import ABCMeta

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
        self.categories.setdefault(category, {})

    def remove_category(self, category):
        del self.categories[category]

    def add_word_to_category(self, category, word, count):
        self.categories[category][word] = self.categories[category].get(word,
            0) + count

    def get_categories(self):
        return self.categories.items()


class RedisStorage(Storage):
    """Store train results in redis database.
    """
