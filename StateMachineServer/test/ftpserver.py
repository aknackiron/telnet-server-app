# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
An example FTP server with minimal user authentication.
"""

from twisted.protocols.ftp import FTPFactory, FTPRealm
from twisted.cred.portal import Portal
from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB
from twisted.internet import reactor

from ipaddr import IPAddress
import threading

#
# First, set up a portal (twisted.cred.portal.Portal). This will be used
# to authenticate user logins, including anonymous logins.
#
# Part of this will be to establish the "realm" of the server - the most
# important task in this case is to establish where anonymous users will
# have default access to. In a real world scenario this would typically
# point to something like '/pub' but for this example it is pointed at the
# current working directory.
#
# The other important part of the portal setup is to point it to a list of
# credential checkers. In this case, the first of these is used to grant
# access to anonymous users and is relatively simple; the second is a very
# primitive password checker.  This example uses a plain text password file
# that has one username:password pair per line. This checker *does* provide
# a hashing interface, and one would normally want to use it instead of
# plain text storage for anything remotely resembling a 'live' network. In
# this case, the file "pass.dat" is used, and stored in the same directory
# as the server. BAD.
#
# Create a pass.dat file which looks like this:
#
# =====================
#   jeff:bozo
#   grimmtooth:bozo2
# =====================
#

from threading import Thread
import logging

class FtpServer:
    # def __init__(self, e):
    #     self.e = e

    logging.basicConfig(level=logging.DEBUG,
        format='(%(threadName)-10s) %(message)s',
        )

    def start(self, e):
        p = Portal(FTPRealm('./'),
                   [AllowAnonymousAccess(), FilePasswordDB("pass.dat")])


        # Once the portal is set up, start up the FTPFactory and pass the
        # portal to it on startup. FTPFactory will start up a
        # twisted.protocols.ftp.FTP() handler for each incoming OPEN
        # request. Business as usual in Twisted land.
        factory = FTPFactory(p)

        self._port = reactor.listenTCP(0, factory, interface=b"127.0.0.1")
        self.ip = IPAddress(self._port.getHost().host)
        self.port = self._port.getHost().port
        logging.debug("a: "+ str(self.ip) +":"+ str(self.port))

        Thread(target=reactor.run, args=(True,)).start()
        # ftp service should be running - set event handler
        if e != None:
            e.set()

    def stop(self):
        self._port.stopListening()


if __name__ == "__main__":
    f = FtpServer()
    f.start(None)
