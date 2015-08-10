from twisted.trial import unittest
import sys, os
import tempfile
from FtpStateMachine import FtpStateMachine
from ftpserver import FtpServer
import threading

####
#
# To start the ftp server locally run this on command line:
# twistd -n ftp
#
#####

class TestFtpStateMachine(unittest.TestCase):
    def setUp(self):
        self.sm = FtpStateMachine()
        # start a local FTP server running on port 2121 and serving
        # current directory
        e = threading.Event()
        self.server = FtpServer()

        # t = threading.Thread(target=self.server.start, args=(e,))
        # t.daemon = True
        self.server.start(e)

        while not e.isSet():
            print "Waiting for ftp service to start"
            import time
            time.sleep(1)
        
        print self.server.ip
        print self.server.port
        self.addCleanup(self.server.stop)


    def tearDown(self):
        self.sm = None

        
    ### FTP states ###
    # def test_actions_allowed_in_state_INIT(self):
    #     self.assertTrue(self.sm._action_allowed_in_state("connect"))

    # def test_actions_allowed_in_state_CONNECTED(self):
    #     self.sm._set_state_to("CONNECTED")
    #     self.assertTrue(self.sm._action_allowed_in_state("login"))

    # def test_actions_allowed_in_state_LOGGED_IN(self):
    #     self.sm._set_state_to("LOGGED_IN")
    #     self.assertTrue(self.sm._action_allowed_in_state("size"))
    #     self.assertTrue(self.sm._action_allowed_in_state("download"))
    #     self.assertTrue(self.sm._action_allowed_in_state("close"))

    # def test_actions_not_allowed_in_state_INIT(self):
    #     self.sm._set_state_to("INIT")
    #     self.assertFalse(self.sm._action_allowed_in_state("login"))
    #     self.assertFalse(self.sm._action_allowed_in_state("cwd"))
    #     self.assertFalse(self.sm._action_allowed_in_state("size"))
    #     self.assertFalse(self.sm._action_allowed_in_state("download"))
    #     self.assertFalse(self.sm._action_allowed_in_state("close"))

    ### Functional tests ### 
    def test_cwd_to_wrong_dir(self):
        """FTP server needs to be running on localhost"""
        result = self.sm.connect(str(self.server.ip) +" "+ str(self.server.port))
        self.assertTrue(result.count("220")>0, "Could not connect to localhost")
        # self.sm.login("john doe")
        # result = self.sm.cwd("NON_EXISTING_DIRECTORY")
        # print "test_cwd_to_wrong_dir - result: {0}".format(result)
        # self.assertTrue(result.count("550")>0, "Wrong response code to cd to wrong directory")
        # self.sm.close()

    def test_clwd(self):
        """change local working directory"""
        # local directory is present
        tmpFile = tempfile.mkdtemp()
        self.assertEquals(self.sm.clwd(tmpFile), tmpFile)

        # wrong local directory
        wrongFile = tmpFile + "/WRONG_PATH"
        result = self.sm.clwd(wrongFile)
        self.assertEquals(result, "No such file or directory")
        import os
        os.rmdir(tmpFile)

    def test_ftp_download_to_tmp_directory(self):
        """Make an FTP download to a tmp folder and check the file came there"""
        result = self.sm.connect("ftp.debian.org")
        self.assertFalse(result.count("NOK")>0, "Connection to ftp server failed!")
        self.sm.login()
        self.sm.cwd("debian")
        # create a temporary local file 
        tmpFile = tempfile.mkdtemp()
        self.sm.clwd(tmpFile)
        self.sm.download("README")
        print "TEST - file downloaded to: %s" % tmpFile+"/README" 
        self.assertTrue(os.path.isfile(tmpFile +"/README"))

    def test_connect_with_port_nro(self):
        """NOTE! FTP server needs to be running at localhost port 2121!!!"""
        result = self.sm.connect("localhost 2121")
        print "test_connect_with_port_nro - result: {0}".format(result)
        self.assertTrue(result.count("220")>0, "Connecting with port gives wrong response: {0}".format(result))

    def test_login_with_params(self):
        """NOTE! FTP server needs to be running at localhost port 2121!!!"""
        result = self.sm.connect("localhost 2121")
        self.assertTrue(result.count("220")>0)
        result = self.sm.login("john doe")
        print "test_login_with_params - "+ result
        self.assertEquals(result, "230 User logged in, proceed")

    def test_ftp_upload_file(self):
        """NOTE! FTP service needs to be running on localhost 2121"""
        upload_dir = tempfile.mkdtemp()
        local_dir = "/tmp"
        local_file = tempfile.mkstemp(suffix=".txt", dir=local_dir)[1]
        result = self.sm.connect("localhost 2121")
        self.assertTrue(result.count("220")>0, "Connect command failed")
        result = self.sm.login("john doe")
        self.assertTrue(result.count("230")>0, "Login did not return OK")
        # change to /tmp on local 
        self.sm.clwd("/tmp")
        # change to upload_dir on remote server
        result = self.sm.cwd(upload_dir)
        print "test_ftp_upload_file - pwd: {0}".format(self.sm.pwd())
        self.assertTrue(result.count("250")>0, "Directory change failed: {0}".format(result))
        filename = os.path.split(local_file)[1] # get only the name without path
        result = self.sm.put(filename)
        self.assertTrue(result.count("226")>0) # transfer completed
        filename = upload_dir + "/"+ filename
        print "test_ftp_upload_file - new file should be: {0}".format(filename)
        self.assertTrue(os.path.isfile(filename))


    ### Error messsages ###
    def test_connect_error_message(self):
        """Tries connecting to unexisting ftp service (localhost 9999)"""
        # Errno 111 - connection refused
        self.assertTrue(self.sm.connect("localhost 9999").find("Errno 111")>0)
        
    def test_cwd_error_message(self):
        cwd_ok = "250 Directory successfully changed."
        self.sm.connect("ftp.debian.org")
        self.sm.login()
        self.assertEquals(self.sm.cwd(""), cwd_ok)
        self.assertEquals(self.sm.cwd("debian"), cwd_ok)



# suite = unittest.TestLoader().loadTestsFromTestCase(TestFtpStateMachine)
# unittest.TextTestRunner(verbosity=2).run(suite)
