from StateMachineServer.RemoteStateMachine import RemoteStateMachineFactory
from twisted.trial import unittest
from twisted.test import proto_helpers


class TestRemoteStateMachine(unittest.TestCase):
    def setUp(self):
        self.factory = RemoteStateMachineFactory()
        self.proto = self.factory.buildProtocol(('localhost', 8123))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

#    def tearDown(self):
#        print "Tear down"

    #### How to set up the network communication ??? ###

    # operation = remote server's method name, data_in & expecte are
    # the input and expected outputs
    def _test(self, operation, data_in, expected):
        self.proto.dataReceived('%s %s\r\n' % (operation, data_in))
        result = self.tr.value().rstrip()
        print "_test received: '%s'" % result
        self.assertEqual(result, expected)
        self.tr.clear()

    # nothing after initialization the server state should be in SETUP
    def test_server_current_state(self):
        self._test('current_state', "", "RUNNING")

    # after "FTP" command the server state should be waiting for FTP commands
    def test_server_switch_state(self):
        self._test('switch_state', "", "END")

    # def test_ftp_connect(self):
    #     self.factory
        

if __name__ == '__main__':
    unittest.main()    


