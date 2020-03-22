import pytz
import logging
import sys
import os
import datetime

loggers = {}


def setup_logger(name, logdir=None, filename_arg=None):
    if not logdir:
        logdir = os.getenv('LOG_DIR', './')

    if 'pytest' in sys.modules:
        logdir = os.path.join(logdir, 'test')
        fmtstr = "[ %(asctime)s ][ %(levelname)s ][%(process)d] - %(message)s"
        filename = name
    else:
        pid = os.getpid()
        logdir = os.path.join(logdir, 'run')
        filename = f'server_run_{pid}'
        fmtstr = f"[ %(asctime)s ][ %(levelname)s ][ %(process)d ][ {name} ] - %(message)s"

    global loggers
    if loggers.get(name):
        return loggers.get(name)
    logger = logging.getLogger(name)
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    time = datetime.datetime.now(pytz.timezone('Asia/Tel_Aviv')).\
        strftime("%b_%d_%Y_%H_%M")
    # logdir = os.path.join(logdir, time)
    # try:
    #     os.mkdir(logdir)
    # except FileExistsError:
    #     pass
    # if filename_arg:
    #     filename = f'{filename_arg}.log'
    # else:
    #     filename = f'{filename}.log'
    # path = os.path.join(logdir, filename)
    # console = logging.FileHandler(path)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=fmtstr)

    console.setFormatter(formatter)
    logger.addHandler(console)
    loggers[name] = logger

    return logger
