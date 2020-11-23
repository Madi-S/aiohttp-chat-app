import logging


formatter = logging.Formatter(
    style='{', fmt='{levelname} - {name} - {asctime} - {pathname} - {lineno} - {message}')

handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def log(f):
    def inner(*args, **kwargs):
        method = f.__name__
        try:
            logger.debug('Method %s was called received: %s and %s',
                         method, args, kwargs)
            return f(*args, **kwargs)
        except Exception:
            logger.exception('Error in method %s:', method, exc_info=True)
            raise

    return inner
