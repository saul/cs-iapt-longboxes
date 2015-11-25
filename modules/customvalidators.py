import re
from gluon.validators import Validator


class IS_FEWER_WORDS(Validator):
    """Validator that ensures the value contains fewer than X words."""

    def __init__(self, max_words,
                 error_message='Must be fewer than %(max_words)d words, you entered %(num_words)d. Please delete %(num_words_to_remove)d word(s).'):
        self.max_words = max_words
        self.error_message = error_message

    def __call__(self, value):
        words = re.findall(r'(\S+(\s+|\s*$))', value)
        num_words = len(words)

        if num_words >= self.max_words:
            return value, self.error_message % {'max_words': self.max_words, 'num_words': num_words, 'num_words_to_remove': (self.max_words - num_words) + 1}

        return value, None
