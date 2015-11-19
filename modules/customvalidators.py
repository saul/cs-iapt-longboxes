from gluon.validators import Validator


class IS_FEWER_WORDS(Validator):
    def __init__(self, max_words,
                 error_message='Must be fewer than %(max_words)d words'):
        self.max_words = max_words
        self.error_message = error_message

    def __call__(self, value):
        if len(value.split()) >= self.max_words:
            return value, self.error_message % {'max_words': self.max_words}

        return value, None
