import os
import unittest
import sys
from StringIO import StringIO
import subprocess
import random
import shutil
# target module to test
import mlogging

#util
def gen_random_string(length=10):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for x in range(10))
def gen_temp_dir(root='/tmp'):
    '''generate a directory which doesn't exist before'''
    while(True):
        temp_dir = os.path.join(root, gen_random_string())
        if not os.path.exists(temp_dir):
            break
    return temp_dir
def get_linestring_split(linestring, index=0):
    '''Return line split list in position index'''
    return linestring.strip().split('\n')[index].split()

# Testcases, generate class by different setup and teardown procedure    
class TestScreenOutput(unittest.TestCase):
    ''' Test screen output function'''

    def test_screen_basic(self):
        # make sure logging to screen works
        name = 'screen.basic'
        log = mlogging.config(name=name, outputs=['screen'])
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.warning('warning')
        log_output = log.handlers[0].stream.getvalue()
        msg_warning = get_linestring_split(log_output, 0)
        self.assertEqual(msg_warning[3:6], [name,'WARNING','warning'])

    def test_screen_filter(self):
        # make sure logging to screen works
        name = 'screen.filter'
        log = mlogging.config(name=name, outputs=['screen'], levels=['warning','debug'])
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.critical('critical')
        log.error('error')
        log.warning('warning')
        log.info('info')
        log.debug('debug')
        log_output = log.handlers[0].stream.getvalue()
        msg_warning = get_linestring_split(log_output,0)
        self.assertEqual(msg_warning[3:6], [name,'WARNING','warning'])
        msg_debug = get_linestring_split(log_output,1)
        self.assertEqual(msg_debug[3:6], [name,'DEBUG','debug'])

class TestLocalOutput(unittest.TestCase):
    ''' Test log to local file'''

    def setUp(self):
        self.local_root = gen_temp_dir()
        mlogging.option('local_root', self.local_root)

    def tearDown(self):
        shutil.rmtree(self.local_root)

    def test_local_basic(self):
        # logging to local file test
        name = 'local.basic'
        log = mlogging.config(name=name, outputs=['local'])
        log.warning('warning')
        log_file = os.path.join(self.local_root, name.replace('.','/'))
        tail = subprocess.Popen(["tail",log_file], stdout=subprocess.PIPE)
        msg = get_linestring_split(tail.stdout.read(), -1)
        self.assertEqual(msg[3:6], [name,'WARNING','warning'])
 
class TestRemoteOutput(unittest.TestCase):
    '''Test remote output'''
   
    def test_remote_basic(self):
        # logging to remote scribe test
        name = 'remote.basic'
        log = mlogging.config(name=name, outputs=['remote'])
        log.warning('warning')

class TestCombineOutput(unittest.TestCase):
    ''' Test log to multiple ends'''

    def setUp(self):
        self.local_root = gen_temp_dir()
        mlogging.option('local_root', self.local_root)

    def tearDown(self):
        shutil.rmtree(self.local_root)

    def test_combine_basic(self):
        # test combined logging
        name = 'combine.basic'
        log = mlogging.config(name=name, outputs=['screen','local'])       
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.warning('warning')
        log_output = log.handlers[0].stream.getvalue()
        screen_msg = log_output.split()
        self.assertEqual(screen_msg[3:6], [name,'WARNING','warning'])
        log_file = os.path.join(self.local_root, name.replace('.','/'))
        tail = subprocess.Popen(["tail",log_file], stdout=subprocess.PIPE)
        msg_local =  get_linestring_split(tail.stdout.read(), -1)
        self.assertEqual(msg_local[3:6], [name,'WARNING','warning'])

if __name__ == '__main__':
#    unittest.main()
    tests = [TestScreenOutput,TestLocalOutput,TestRemoteOutput,TestCombineOutput]
    suites = []
    for test in tests:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))
    all_suites = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(all_suites)
