import sys, os


path = os.path.dirname(__file__)
if sys.path.count(path) == 0:
    sys.path.insert(0, path)
print "Current path:\n%s" % sys.path
from StateMachineServer import RemoteStateMachine

sm = RemoteStateMachine.main()
