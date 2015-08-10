import os
from ftplib import FTP, error_perm

### State machine definition for FTP transfer #################
# 
# FTP state machine lifecycle is as follows:
# INIT -> CONNECTED -> LOGGED_IN -> INIT
#
#
# Note, each new function in this class needs to be "published" in the
# private method _action_allowed_in_state() and in the remote-methods
# of the RemoteServer class handling this class.
#
###############################################################


class FtpStateMachine(object):
    def __init__(self):
        print "FtpStateMachine - started."
        self.state = "INIT"  
        self.ftp = FTP()

    def connect(self, hostname):
        """Tries to create FTP connection to the received hostname
        parameter. In case of connection error, error message is sent
        back. For success OK is sent back."""
        result = ""
        if self._action_allowed_in_state('connect'):
            portnro = None
            if len(hostname.split(" ")) > 1:
                hostname, portnro = hostname.split(" ")
            try:
                if portnro:
                    print "FtpStateMachine - tries to connect with host '{0}' and port '{1}''".format(hostname, portnro)
                    result = self.ftp.connect(hostname, portnro)
                else:
                    print "FtpStateMachine - tries to connect to host '{0}'".format(hostname)
                    result = self.ftp.connect(hostname)
            except (EOFError, IOError) as error:
                errorMsg = "FtpStateMachine - NOK: '%s'" % error
                print errorMsg
                return errorMsg
            except:
                print "FtpStateMachine - connect - Unexpected error!"
            self._set_state_to("CONNECTED")
            return result
        else:
            return "FTP statemachine not started!"

    def login(self, params=""):
        """Login to the FTP server. Optional parameter 'params' can
        contain 'username passwd' space separated tuple."""
        result = ""
        if self._action_allowed_in_state('login'):
            _user = None
            _pwd = None
            # TODO throw error if wrong number of params!
            if len(params.split(" ")) == 2:
                _user, _pwd = params.split(" ")
            if not _user or not _pwd:
                result = self.ftp.login()
            else:
                result = self.ftp.login(user=_user, passwd=_pwd)
            self._set_state_to("LOGGED_IN")
        return result

    def cwd(self, dirname):
        """Change working directory on the FTP server. New directory
        is returned as response."""
        result = ""
        if self._action_allowed_in_state('cwd'):
            try:
                print "FtpStateMachine - cwd - changing to: {0}".format(dirname)
                result = self.ftp.cwd(dirname)
            except error_perm as error:
                return "{0}".format(error)
        return result

    def pwd(self):
        result = "OK"
        try:
            print("FtpStateMachine - pwd")
            result = self.ftp.pwd()
        except error_perm as error:
            result = "{0}".format(error)
            print("pwd - error: '{0}'".format(result))
        return result
    
    def clwd(self, dirname):
        """Takes the local directory name where we should change to."""
        self.lastDir = os.getcwd()
        # does dirname location exist - yes/no?
        try: 
            os.chdir(dirname)
        except OSError as error:
            return error.strerror
        return dirname
    
    def size(self, filename):
        size = -1
        if self._action_allowed_in_state('size'):
            size = self.ftp.size(filename)
        return size

    def download(self, filename):
        # need to change to some local directory before?
        # self.ftp.cwd('debian')
        result = "DOWNLOAD FAILS"
        if self._action_allowed_in_state('download'):
            try:
                result = self.ftp.retrbinary('RETR '+ filename, open(filename, 'wb').write)
            except error_perm as error:
                return "NOK - {0}".format(error)
        return result

    def put(self, filename):
        """Sends local file to remote FTP server."""
        result = ""
        print "FtpStateMachine - put command received {0}".format(filename)
        extension = os.path.splitext(filename)[1]
        print "FtpStateMachine - upload file '{0}' with extension '{1}'".format(filename, extension)
        try:
            if extension in (".txt", ".htm", ".html"):
                fileToSend = open(filename)
                result = self.ftp.storlines("STOR " + filename, fileToSend)
            else:
                fileToSend = open(filename, "rb")
                result = self.ftp.storbinary("STOR " + filename, fileToSend, 1024)
        except error_perm as error:
            return "NOK - {0}".format(error)
        return result

    def close(self):
        result = ""
        if self._action_allowed_in_state('close'):
            result = self.ftp.close()
            self._set_state_to("INIT")
        return result

    ### Private methods #################

    def _set_state_to(self, new_state):
        # todo, some check if state transition is possible?
        self.state = new_state

    def _action_allowed_in_state(self, method):
        """
        What can and cannot be done in each FTP state
        INIT - only a connect command can be done
            * connect - make connection to an FTP server
        CONNECTED - only login can be done
            * login - login to the server
        LOGGED_IN - any ftp command currently supported:
            * size - return the size of a file
            * cwd - return the new working directory path 
            * download - download a file from server
            * close - close the current ftp connection to server
        """
        if self.state == "INIT" and method in ['connect']:
            return True
        elif self.state == "CONNECTED" and method in ['login']:
            return True
        elif self.state == "LOGGED_IN" and method in ['size', 'cwd', 'download', 'close', 'put', 'pwd']:
            return True
        else:
            return False

    
