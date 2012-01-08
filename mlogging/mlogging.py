'''mlogging module'''
import os
import logging
try:
    from scribe_logger.logger import ScribeLogHandler
    enable_scribe = True
except ImportError:
    enable_scribe = False

# mlogging config
format_string =  '%(asctime)s %(module)s %(name)s %(levelname)s %(message)s'
local_root =  '/tmp'
scribe_host = '127.0.0.1'
scribe_port = 1456

def option(name,value):
    options = ['format_string','local_root', 'scribe_host', 'scribe_port']
    if not name in options:
        return
    globals()[name] = value    
            
def config(name='default', outputs=['screen'], levels=['all']):
    '''Config a logger

    output: a list of output types, they can be
        * screen: output to screen
        * local: local file in log_dir_local
        * remote: remote path using scribe
    filter: a list of level to be shown they can be
        all, debug, info, warning, error, critical
    '''
    global local_root
    logger = logging.getLogger(name)
    # reset log handlers
    for h in logger.handlers:
        logger.removeHandler(h)
    # default record all level info
    logger.setLevel(logging.DEBUG)
    for op in outputs:
        if op == 'screen':
            logger.addHandler(get_screen_handler())
        elif op == 'local':
            logger.addHandler(get_local_handler(name))
        elif op == 'remote' and enable_scribe:
            logger.addHandler(get_remote_handler(name))
    levelmap = {'debug':logging.DEBUG,
                'info':logging.INFO,
                'warning':logging.WARNING,
                'error':logging.ERROR,
                'critical':logging.CRITICAL}
    logging_level = []
    for lvl in levels:
        if lvl == 'all':
            logging_level.extend(levelmap.values())
            break
        log_lvl = levelmap.get(lvl,None)
        if log_lvl:
            logging_level.append(log_lvl)
    logging_level = set(logging_level)
    logger.addFilter(MultipleFilter(logging_level))
    return logger

class MultipleFilter(logging.Filter):
    '''Choose log which level in logging_level'''
    def __init__(self, logging_level):
        self.logging_level = logging_level
        logging.Filter.__init__(self)
    def filter(self, record):
        return record.levelno in self.logging_level

def get_screen_handler():
    '''Return a screen appender of loggging'''
    global format_string
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_string))
    return handler

def get_local_handler(name):
    '''Return handler write to local file'''
    global formatter, local_root
    log_file = os.path.join(local_root, name.replace('.','/'))
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    handler = logging.FileHandler( log_file, 'a')
    handler.setFormatter(logging.Formatter(format_string))
    return handler

def get_remote_handler(name):
    '''Return handler write to remote file'''
    global formatter, scribe_host, scribe_port
    handler = ScribeLogHandler(category=name, host=scribe_host, port=scribe_port)
    handler.setFormatter(logging.Formatter(format_string))
    return handler

def get_null_handler():
    ''' Dummy handler to avoid no handler warning'''
    handler = logging.FileHandler('/dev/null','w')
    return handler

def reset(name):
    '''Reset log to forbid all handler output and no handler warning'''
    log = logging.getLogger(name)
    for h in log.handlers:
        log.removeHandler(h)
    log.addHandler(get_null_handler())
