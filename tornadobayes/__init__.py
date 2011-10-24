import re
import math

from brukva import Client

NON_ALPHA = re.compile(r'[^\w\.]', re.IGNORECASE)
ONE_OR_TWO_WORDS = re.compile(r'\b[^\s]{1,2}\b', re.IGNORECASE)

class BayesBaseClient(object):

    def __init__(self):
        self.categories = {}

    def train(self, data, category):
        category = category.lower()
        self.add_category(category)

        for word, count in self.count_occurance(data):
            self.add_word_to_category(category, word, count)

    def add_word_to_category(self, category, word, count):
        self.categories[category][word] = self.categories[category].get(word, 0) + count

    def count_occurance(self, text=''):
        sep_by_non_alpha = NON_ALPHA.sub(' ', text.lower())
        without_one_or_two_words = ONE_OR_TWO_WORDS.sub('', sep_by_non_alpha)
        without_dots = without_one_or_two_words.replace('.', '')
        text_chunks = without_dots.split()

        freqs = {}
        for word in text_chunks:
            freqs[word] = freqs.get(word, 0) + 1
        return freqs.items()

    def add_category(self, category):
        self.categories.setdefault(category, {})

    def remove_category(self, category):
        del self.categories[category]

    def get_categories(self, return):
        return self.categories.items()

    def classify(self, data):
        scores = {}
        for category, words in self.get_categories():
            words_count_per_category = reduce(lambda x,y: x+y,
                map(float, words.values()))

            if words_count_per_category == 0:
                self.remove_category(category)

            scores[category] = 0
            for word, count in self.count_occurance(data):
                tmp_score = words.get(word)
                if tmp_score and float(tmp_score) > 0.0:
                    tmp_score = float(tmp_score)
                else:
                    tmp_score = 0.1

                scores[category] += tmp_score / words_count_per_category

        return scores


class BayesRedisClient(BayesBaseClient):

    def __init__(self, redis_host, redis_port):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_client = Client(redis_host, redis_port)
        self.redis_client.connect()

    def swith_db(self, db_index):
        self.redis_client.select(db_index)
