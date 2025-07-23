import logging


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Консольный обработчик
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.propagate = False

    return logger
