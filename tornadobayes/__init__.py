import re
import math

from tornadobayes import storage

NON_ALPHA = re.compile(r'[^\w\.]', re.IGNORECASE)
ONE_OR_TWO_WORDS = re.compile(r'\b[^\s]{1,2}\b', re.IGNORECASE)

class BayesClient(object):

    def __init__(self, storage_class, *args, **kwargs):
        self.storage = storage_class(*args, **kwargs)

    def train(self, data, category):
        category = category.lower()
        self.storage.add_category(category)

        for word, count in self.count_occurance(data):
            self.storage.add_word_to_category(category, word, count)

    def count_occurance(self, text=''):
        sep_by_non_alpha = NON_ALPHA.sub(' ', text.lower())
        without_one_or_two_words = ONE_OR_TWO_WORDS.sub('', sep_by_non_alpha)
        without_dots = without_one_or_two_words.replace('.', '')
        text_chunks = without_dots.split()

        freqs = {}
        for word in text_chunks:
            freqs[word] = freqs.get(word, 0) + 1
        return freqs.items()


    def classify(self, data):
        scores = {}
        for category, words in self.storage.get_categories():
            words_count_per_category = reduce(lambda x,y: x+y,
                map(float, words.values()))

            if words_count_per_category == 0:
                self.storage.remove_category(category)

            scores[category] = 0
            for word, count in self.count_occurance(data):
                tmp_score = words.get(word)
                if tmp_score and float(tmp_score) > 0.0:
                    tmp_score = float(tmp_score)
                else:
                    tmp_score = 0.1

                scores[category] += tmp_score / words_count_per_category

        return scores
