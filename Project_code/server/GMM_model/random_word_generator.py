from random_words import RandomWords
import sys
import os
import random
from fuzzywuzzy import fuzz

class Random_Generator(object):
    rw = RandomWords()

    def generate_words(self):
        count = random.randint(7,10)
        words = self.rw.random_words(count = count)
        return words

    def check_words(self, goog_str, words):
        words_string = " ".join(words)
        ratio = fuzz.ratio(goog_str, words_string)
        if ratio >=90:
            return True
        return False


if __name__ == '__main__':
    word_list = generate_words()
    print word_list
    sys.exit(0)