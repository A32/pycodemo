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

class TestMLogging(unittest.TestCase):
    ''' Test mlogging'''

    def test_screen_logging(self):
        # make sure logging to screen works
        name = 'screentest1'
        log = mlogging.config(name=name, outputs=['screen'], levels=['warning','debug'])
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.warning('warning')
        log.info('info')
        log.debug('debug')
        log_output = log.handlers[0].stream.getvalue()
        msg_warning = log_output.strip().split('\n')[0].split()
        self.assertEqual(msg_warning[3:6], [name,'WARNING','warning'])
        msg_debug = log_output.strip().split('\n')[1].split()
        self.assertEqual(msg_debug[3:6], [name,'DEBUG','debug'])
        mlogging.reset(name)
        
 
    def test_local_logging(self):
        # logging to local file test
        local_root = gen_temp_dir()
        name = 'local.test.test'
        log = mlogging.config(name=name, outputs=['local'], local_root=local_root)
        log.warning('warning')
        log_file = os.path.join(local_root, name.replace('.','/'))
        tail = subprocess.Popen(["tail",log_file], stdout=subprocess.PIPE)
        msg = tail.stdout.read().strip().split('\n')[-1].split()
        self.assertEqual(msg[3:6], [name,'WARNING','warning'])
        shutil.rmtree(local_root)
        mlogging.reset(name)
        
    def test_combine_logging(self):
        # test combined logging
        local_root = gen_temp_dir()
        name = 'local.test.test'
        log = mlogging.config(name=name, outputs=['screen','local'], local_root=local_root)       
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.warning('warning')
        log_output = log.handlers[0].stream.getvalue()
        screen_msg = log_output.split()
        self.assertEqual(screen_msg[3:6], [name,'WARNING','warning'])
        log_file = os.path.join(local_root, name.replace('.','/'))
        tail = subprocess.Popen(["tail",log_file], stdout=subprocess.PIPE)
        msg_local = tail.stdout.read().strip().split('\n')[-1].split()
        self.assertEqual(msg_local[3:6], [name,'WARNING','warning'])
        shutil.rmtree(local_root)
        mlogging.reset(name)

if __name__ == '__main__':
#    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMLogging)
    unittest.TextTestRunner(verbosity=2).run(suite)
