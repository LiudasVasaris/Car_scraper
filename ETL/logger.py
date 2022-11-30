import logging

# create LOGGER
LOGGER = logging.getLogger("simple_example")
LOGGER.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s]: %(message)s"
)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to LOGGER
LOGGER.addHandler(ch)
