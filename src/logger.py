import logging
import os

class Logger:
    logger = None

    @classmethod
    def create_logger(cls, log_level_string):
        # TODO: move log into a new log/ folder
        if os.path.exists('RimTranslate.log'):
            os.remove('RimTranslate.log')

        log_format = '%(levelname)s: %(message)s' 
        log_level = getattr(logging, str.upper(log_level_string))

        logging.basicConfig(
            format=log_format,
            level=log_level,
            filename='RimTranslate.log' # TODO: change log name to not be too close to runtime name
        )

        # TODO: set streamhandler to not output to stderr by default
        #       https://docs.python.org/3/library/logging.handlers.html#logging.StreamHandler
        console = logging.StreamHandler()
        console.setLevel(log_level)
        console.setFormatter(logging.Formatter(log_format))

        cls.logger = logging.getLogger('main')
        cls.logger.addHandler(console)

        return cls.logger

    @classmethod
    def get_logger(cls):
        return cls.logger
