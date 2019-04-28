import logging
from colorlog import ColoredFormatter   # install using sudo pip3 install colorlog

logger = logging.getLogger('pythonConfig')

def initialize(loggingRootDir=None):
    LOG_LEVEL = logging.INFO
    if loggingRootDir != None:
        logfile = '%s\\log.txt' % loggingRootDir
        with open(logfile, 'w'): pass # clear logfile
        logging.basicConfig(filename=logfile, level=logging.INFO)
    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(
        "  %(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s%(reset)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'white,bg_red',
        },
        secondary_log_colors={},
        style='%'
    )
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(stream)