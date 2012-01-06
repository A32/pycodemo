'''papaya logging module'''
import os
import logging

_default_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
_default_local_root = '/tmp'

def config(name='default', output=['screen'], level=['all'],local_root=_default_local_root):
    '''Config a logger

    output: a list of output types, they can be
        * screen: output to screen
        * local: local file in log_dir_local
        * remote: remote path using scribe
    filter: a list of level to be shown they can be
        all, debug, info, warning, error, critical
    '''
    logger = logging.getLogger(name)
    for op in output:
        if op == 'screen':
            logger.addHandler(_screen_handler)
        elif op == 'local':
            logger.addHandler(get_local_handler(name, local_root))
    return logger

def get_screen_handler():
    '''Return a screen appender of loggging'''
    handler = logging.StreamHandler()
    handler.setFormatter(_default_formatter)
    return handler
_screen_handler = get_screen_handler()

def get_local_handler(name,local_root):
    '''Return handler write to local file'''
    log_file =  os.path.join(local_root, name.replace('.','/'))
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedir(log_dir)
    handler = logging.FileHandler( log_file, 'a')
    handler.setFormatter(_default_formatter)
    return handler

def get_null_handler():
    handler = logging.FileHandler('/dev/null','w')
    return handler

def reset(name):
    log = logging.getLogger(name)
    for h in log.handlers:
        log.removeHandler(h)
    log.addHandler(get_null_handler())
