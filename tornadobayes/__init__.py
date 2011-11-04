import re
import math
from functools import partial

from tornadotools import adisp

from tornadobayes import storage

NON_ALPHA = re.compile(r'[^\w\.]', re.IGNORECASE | re.UNICODE)
ONE_OR_TWO_WORDS = re.compile(r'\b[^\s]{1,2}\b', re.IGNORECASE | re.UNICODE)

class BayesClient(object):

    def __init__(self, storage_obj):
        self.storage = storage_obj 

    @adisp.async
    @adisp.process
    def train(self, data, category, callback=None):
        yield self.storage.add_category(category)
        category_words = {}
        for word, count in self.__count_occurance(data):
            category_words[word] = count
        yield self.storage.add_words_to_category(category, category_words)
        callback({'result': 'OK'})

    def __count_occurance(self, text=''):
        sep_by_non_alpha = NON_ALPHA.sub(' ', text.lower())
        without_one_or_two_words = ONE_OR_TWO_WORDS.sub('', sep_by_non_alpha)
        without_dots = without_one_or_two_words.replace('.', '')
        text_chunks = without_dots.split()
        freqs = {}
        for word in text_chunks:
            freqs[word] = freqs.get(word, 0) + 1
        return freqs.items()


    @adisp.async
    @adisp.process
    def classify(self, data, callback=None):
        scores = {}
        categories = yield self.storage.get_categories()
        for category, words in categories:
            words_count_per_category = reduce(lambda x,y: x+y,
                map(float, words.values()))

            if words_count_per_category == 0:
                yield self.storage.remove_category(category)

            scores[category] = 0
            for word, count in self.__count_occurance(data):
                tmp_score = words.get(word)
                if tmp_score and float(tmp_score) > 0.0:
                    tmp_score = float(tmp_score)
                else:
                    tmp_score = 0.1

                scores[category] += tmp_score / words_count_per_category
        import pdb;pdb.set_trace()
        callback(scores)
