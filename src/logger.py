import logging
import os

class Logger:
    logger = None

    @classmethod
    def init(cls, log_level_string):
        os.makedirs('logs/', exist_ok=True)
        if os.path.exists('logs/RimTranslate.log'):
            os.remove('logs/RimTranslate.log')

        log_format = '%(levelname)s: %(message)s' 
        log_level = getattr(logging, str.upper(log_level_string))

        logging.basicConfig(
            format=log_format,
            level=log_level,
            filename='logs/RimTranslate.log'
        )

        # TODO: set streamhandler to not output to stderr by default
        #       https://docs.python.org/3/library/logging.handlers.html#logging.StreamHandler
        console = logging.StreamHandler()
        console.setLevel(log_level)
        console.setFormatter(logging.Formatter(log_format))

        cls.logger = logging.getLogger('main')
        cls.logger.addHandler(console)

        return cls.logger
