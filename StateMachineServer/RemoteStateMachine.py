### State machine definition for the wrapper protocol #########
# 
# This wrapper state machine can be in states: RUNNING -> END
#
# When in state RUNNING, a client protocol can be started and all
# commands are passed to it. 
#
# In this first implementation only one FTP protocol is
# supported. These can be called when in state RUNNING and the
# commands are prefixied with string "FTP".
# 
# This remote server is commanded with the switch_state-method that
# moves this from STARTED to RUNNING to END. This server closes
# connections and dies when in state END.
###############################################################

from twisted.protocols import basic
from twisted.internet import protocol
from StateMachineServer.FtpStateMachine import FtpStateMachine
from StateMachineServer.SmsService import SmsService
import sys
from socket import gethostbyname, gaierror

class StateMachineProxy(object):
    def __init__(self):
        print "HELLO WORLD!!!"
        self.ftpClient = FtpStateMachine()

        # FTP commands
        self.ftp_commands = ['connect', 'login', 'cwd',
                        'size', 'download', 'close',
                        'clwd', 'put', 'pwd']
        
        for m in self.ftp_commands:
            setattr(self, 'remote_ftp_%s' % m, getattr(self.ftpClient, m))

        # SMS commands
        self.sms_commands = None
        try:
            from StateMachineServer.SmsService import SmsService
            self.smsService = SmsService()

            self.sms_commands = ['send_message_str', 'send_message',
                            'find_new_message', 'start_call',
                            'make_sms_message', 'track_phone_state',
                            'read_phone_state', 'stop_tracking_phone_state']
            for m in self.sms_commands:
                setattr(self, 'remote_sms_%s' % m, getattr(self.smsService, m))
        except (ImportError, gaierror) as error:
            print("SMS service is not available on this platform: {0}".format(error))
        except:
            print("Unexpected error: ", sys.exc_info()[0])
            raise
        


class RemoteStateMachineProtocol(basic.LineReceiver):
    def __init__(self):
        self.state = "RUNNING" # "STARTED"
        self.proxy = StateMachineProxy()
        self._printHelp()

    def lineReceived(self, line):
        line = line.strip()
        # ignore empty lines
        if len(line) == 0:
            return
        print "Received input line: '%s'" % line
        if self.state == "STARTED":
            # can only receive the switch state command
            print "Proxy state is 'STARTED'"
            if not self._handleProxyCommands(line):
                # should something be sent to client?
                msg = "Unknown command '%s'" % line
                msg = msg + "Print help by typing '?' or 'help'.\n"
                return msg
        elif self.state == "RUNNING":
            # forward all commands to the appropriate sub-state machine
            # for handling - execpt if switch state to END is called
            if self._handleProxyCommands(line):
                return

        #### from here on commands are passed to appropriate message handler ###
        # handle ftp client commands
        if hasattr(self.proxy, "remote_ftp_"+ line.split()[0]): 
            self._handle_ftp_commands(line)
        # handle sms commands
        elif hasattr(self.proxy, "remote_sms_"+ line.split()[0]): 
            self._handle_sms_commands(line)
        else:
            print "Not a known operation or command!"



    def current_state(self):
        self.sendLine(str(self.state))

    def switch_state(self):
        print "Changing state from '%s'" % self.state
        if self.state == "STARTED":
            self.state = "RUNNING"
        elif self.state == "RUNNING":
            self.state = "END"
        self.sendLine(str(self.state))
        if self.state == "END":
            self._closeConnection()

    ##### private methods follow #####

    def _handle_sms_commands(self, line):
        result = None
        op_and_params = self._split_to_operation_params(line)
        op = op_and_params[0]
        params  = op_and_params[1]
        print("RemoteStateMachine - op: '{0}' with params: '{1}'".format(op, params))
        # first parameter value is number to sms to, the rest is message body
        try:
            op = getattr(self.proxy, 'remote_sms_%s' % op)
            if len(params) == 0:
                result = op()
            else:
                result = op(params)
        except() as error:
            result = "Command error: {0}".format(error)
            self.sendLine(str(error))
        self.sendLine(str(result))
        return
    
    def _handle_ftp_commands(self, line):
        result = None
        op_and_params = self._split_to_operation_params(line)
        op = op_and_params[0]
        data = op_and_params[1]
        print("RemoteStateMachine - op: '{0}' with params: '{1}'".format(op, data))
        try:
            op = getattr(self.proxy, 'remote_ftp_%s' % op)
            if len(data) == 0:
                result = op()
            else:
                result = op(data)
            print "RemoteStateMachine responded: '%s'" % result
        except (AttributeError, TypeError) as error:
            result = "Command error: {0}".format(error)
        self.sendLine(str(result))
        return

    def _split_to_operation_params(self, line):
        op_params = [None] * 2
        params = line.split()
        op_params[0] = params.pop(0)
        op_params[1] = ' '.join(map(str, params))
        return op_params

    def _printHelp(self):
        msg = "Possible commands for server are: 'switch_state' (or 'quit') or 'current_state'\n"
        print(str(msg))

    # check if state change was requested
    def _closeConnection(self):
        self.transport.loseConnection()

    def _handleProxyCommands(self, line):
        if self._handleSwitchState(line) or \
        self._handleCurrentState(line) or \
        self._handleHelp(line):
            return True
        return False

    def _handleSwitchState(self, param):
        param = param.strip()
        if param == "switch_state" or param == "quit":
            self.switch_state()
            return True
        return False

    def _handleCurrentState(self, line):
        line = line.strip()
        if line == "current_state":
            self.current_state()
            return True
        return False

    def _handleHelp(self, line):
        line = line.strip()
        if line == "help" or line == "?":
            self._printCmdHelp()
            return True
        return False

    def _printCmdHelp(self):
        msg = "Available commands are:\n"
        msg = msg + "FTP commands:{0}".format(self.proxy.ftp_commands)
        if self.proxy.sms_commands is not None:
            msg = msg + "\n" + "SMS commands: \n{0}".format(self.proxy.sms_commands)
        self.sendLine(str(msg))
        return
    
    # checks if the wanted state is a supported (STARTED -> RUNNING -> END)
    def _is_ok_state(self, state):
        if state in ['STARTED', 'RUNNING', 'END']:
            return True
        return False


class RemoteStateMachineFactory(protocol.Factory):
    protocol = RemoteStateMachineProtocol


def main():
    from twisted.internet import reactor
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    reactor.listenTCP(8123, RemoteStateMachineFactory())
    reactor.run()


if __name__ == "__main__":
    main()
