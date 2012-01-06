import os
import unittest
import sys
from StringIO import StringIO
import subprocess
# test case require
import mlogging

class TestMLogging(unittest.TestCase):
    ''' Test ppylogging'''

    def test_screen_logging(self):
        # make sure logging to screen works
        name = 'screentest'
        log = mlogging.config(name=name, output=['screen'])
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.warning('warning')
        log_output = log.handlers[0].stream.getvalue()
        msg = log_output.split()
        self.assertEqual(msg[2:5], [name,'WARNING','warning'])
        mlogging.reset(name)
 
    def test_local_logging(self):
        # logging to local file test
        local_root = '/tmp'
        name = 'local.test.test'
        log = mlogging.config(name=name, output=['local'], local_root=local_root)
        log.warning('warning')
        log_file = os.path.join(local_root, name.replace('.','/'))
        tail = subprocess.Popen(["tail",log_file], stdout=subprocess.PIPE)
        msg = tail.stdout.read().strip().split('\n')[-1].split()
        self.assertEqual(msg[2:5], [name,'WARNING','warning'])
        os.remove(log_file)
        mlogging.reset(name)
 
    def test_combine_logging(self):
        # test combined logging
        local_root = '/tmp'
        name = 'local.test.test'
        log = mlogging.config(name=name, output=['screen','local'], local_root=local_root)       
        # redirect stream to string io to capture
        log.handlers[0].stream = StringIO()
        log.warning('warning')
        log_output = log.handlers[0].stream.getvalue()
        screen_msg = log_output.split()
        self.assertEqual(screen_msg[2:5], [name,'WARNING','warning'])
        log_file = os.path.join(local_root, name.replace('.','/'))
        tail = subprocess.Popen(["tail",log_file], stdout=subprocess.PIPE)
        msg_local = tail.stdout.read().strip().split('\n')[-1].split()
        self.assertEqual(msg_local[2:5], [name,'WARNING','warning'])
        os.remove(log_file)
        mlogging.reset(name)

if __name__ == '__main__':
#    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMLogging)
    unittest.TextTestRunner(verbosity=2).run(suite)
