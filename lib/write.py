def log():
    import logging; from colorlog import ColoredFormatter
    formatter = ColoredFormatter(
        "%(thin_white)s[%(bold_red)s%(asctime)s%(thin_white)s] [%(log_color)s%(levelname)s%(thin_white)s] %(thin_white)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red"
        },
    )
    logger = logging.getLogger("Application")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

