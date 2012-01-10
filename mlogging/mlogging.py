'''mlogging logging module

mlogging supports a simple operation on python logging module. It supports write
log to screen, local file and remote scribe server.

Here is an hello world example for mlogging::

    import mlogging
    log = mlogging.config('mylog',['screen'])
    log.info('hello world')

'''
import os
import logging
try:
    from scribe_logger.logger import ScribeLogHandler
    enable_scribe = True
except ImportError:
    enable_scribe = False

# mlogging config
default_format_string = '%(asctime)s %(module)s %(name)s %(levelname)s %(message)s'
default_local_root =  '/tmp'
default_scribe_host = '127.0.0.1'
default_scribe_port = 1456

def set_default(**kwargs):
    '''Set default value for mlogging configure

    Default value used by config function:

    format_string(logging formatter string), local_root(local path for writing log file)
    scribe_host(scribe server ip address) and  scribe_port(scribe server port)

    For example::
        
        import mlogging
        mlogging.set_default(format_string='%(message)s')
        log = mlogging.config('messageonly', ['screen'])
        log.info('some info')
        # screen shows: some info

    '''
    options = ['format_string','local_root', 'scribe_host', 'scribe_port']
    for k,v in kwargs.items():
        if not k in options:
            continue
        globals()['default_' + k] = v

def option(name, **kwargs):
    '''Change option for specific logger.

    support option includes format_string(logging formatter string), 
    local_root(local path for writing log file), scribe_host(scribe server ip address) and
    scribe_port(scribe server port), scribe_category(scribe category name)

    For example::

        import mlogging
        log = mlogging.config('mylog',['local'])
        mlogging.option('mylog', local_root='/tmp/mylog')
        log.info('some info')

    '''
    options = ['format_string','local_root', 'scribe_host', 'scribe_port', 'scribe_category']
    logger = logging.getLogger(name)
    if 'local_root' in kwargs.keys():
        exist = False
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                exist = True
        if exist:
            logger.addHandler(get_local_handler(name, kwargs.get('local_root')))
    if 'scribe_host' in kwargs.keys() and 'scirbe_port' in kwargs.keys():
        exist = False
        host = kwargs.get('scribe_host')
        port = kwargs.get('scribe_port')
        for handler in logger.handlers:
            if isinstance(handler, logging.ScribeHandler):
                logger.removeHandler(handler)
                exist = True
        if exist:
            logger.addHandler(get_remote_handler(name, host, port))
    if 'scribe_category' in kwargs.keys():
        for handler in logger.handlers:
            if isinstance(handler, logging.ScribeHandler):
                handler.category = kwargs.get('scribe_category')
    if 'format_string' in kwargs.keys():
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(kwargs.get('format_string')))

def config(name='default', outputs=['screen'], levels=['all']):
    '''Config a logger.

    output: a list of output types, they can be
        * screen: output to screen
        * local: local file in log_dir_local
        * remote: remote path using scribe
        * remote_by_host: remote category will add ip information

    levels: a list of level to be shown they can be all, debug, info, warning, error, critical
    levels is DIFFERENT from logging level set. It records levels in this list.

    For example::

        import mlogging
        log = mlogging.config('fileinfolog',['local'],['info'])
        log.info('info is recorded')
        log.warning('warning is not recorded')

    You can reconfig a logger easily by call config again.

    '''
    global default_local_root, default_scribe_host, default_scribe_port
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
            logger.addHandler(get_local_handler(name, default_local_root))
        elif op == 'remote':
            if not enable_scribe:
                print 'mlogging: module scribe_logger not found, can not output to remote'
                continue
            logger.addHandler(get_remote_handler(name, default_scribe_host, default_scribe_port))
        elif op == 'remote_by_host':
            if not enable_scribe:
                print 'mlogging: module scribe_logger not found, can not output to remote'
                continue
            logger.addHandler(get_remote_handler(name, default_scribe_host, default_scribe_port, byhost=True))
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
    global default_format_string
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(default_format_string))
    return handler

def get_local_handler(name, local_root=default_local_root):
    '''Return handler write to local file'''
    global default_format_string
    log_file = os.path.join(local_root, name.replace('.','/'))
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    handler = logging.FileHandler( log_file, 'a')
    handler.setFormatter(logging.Formatter(default_format_string))
    return handler

def get_remote_handler(name, scribe_host=default_scribe_host, scribe_port=default_scribe_port, byhost=False):
    '''Return handler write to remote file'''
    global default_format_string
    if byhost:
        host_name = socket.gethostname()
        dot_pos = hostname.find('.')
        if dot_pos > 0:
            host_name = host_name[:dot_pos]
        category = '.'.join([name,host_name])
    else:
        category = name
    handler = ScribeLogHandler(category=category, host=scribe_host, port=scribe_port)
    handler.setFormatter(logging.Formatter(default_format_string))
    return handler

def get_null_handler():
    ''' Dummy handler to avoid no handler warning'''
    handler = logging.FileHandler('/dev/null','w')
    return handler

def reset(name):
    '''Reset log to forbid all handler output.

    Forbid all output for some logger. So everything produced by this name logger is dropped.
    '''
    log = logging.getLogger(name)
    for h in log.handlers:
        log.removeHandler(h)
    log.addHandler(get_null_handler())
