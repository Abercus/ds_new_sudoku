#!/usr/bin/python

# Setup Python logging ------------------ -------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports ---------------------------------------------------------------------
from server_common import read_games_from_file
import multiprocessing
import protocol
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as soc_error
from sys import exit
import Pyro4
import threading
import time
from socket import IPPROTO_IP, IPPROTO_UDP, IP_MULTICAST_LOOP, IP_MULTICAST_TTL, SOCK_DGRAM
from application.common import MC_IP, MC_PORT, WHOISHERE

# Constants -------------------------------------------------------------------
___NAME = 'Sudoku Server'
___VER = '0.1.0.0'
___DESC = 'Sudoku Server (TCP version)'
___BUILT = '2017-11-01'
___VENDOR = 'Copyright (c) 2017'


# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)
# Not a real main method-------------------------------------------------------
def server_main(args):
    '''Runs the Sudoku server
    @param args: ArgParse collected arguments
    '''
    # Starting server
    LOG.info('%s version %s started ...' % (___NAME, ___VER))

    # Declaring TCP socket
    __server_socket = socket(AF_INET,SOCK_STREAM)
    LOG.debug('Server socket created, descriptor %d' % __server_socket.fileno())
    # Bind TCP Socket

    print(args)
    sock_address = ("127.0.0.1",args.port)

    try:
        __server_socket.bind(sock_address)
    except soc_error as e:
        LOG.error('Can\'t start Sudoku server, error : %s' % str(e) )
        exit(1)
    LOG.debug('Server socket bound on %s:%d' % __server_socket.getsockname())
    # Put TCP socket into listening state
    __server_socket.listen(7000)
    LOG.info('Accepting requests on TCP %s:%d' % __server_socket.getsockname())

    # Declare client socket, set to None
    client_socket = None
    # Declare list of all active game sessions
    sessions = {}
    # Declare list for all names in active use
    names = []
    # Declare list of Client objects
    users = []
    # Declare list of all possible sudoku boards
    fn = 'application/server/sudoku_db'
    boards=read_games_from_file(fn)
    # Declare Pyro4 daemon in separate thread
    daemon = URIhandler()
    daemon.start()
    # Start new thread to advertise server
    broadcaster = BroadcastHandler(sock_address)
    broadcaster.start()

    # Serve forever
    while 1:
        try:
            LOG.debug('Awaiting new client connections ...')
            # Accept client's connection store the client socket into
            # client_socket and client address into source
            client_socket,source = __server_socket.accept()	#Change as required by service discovery
            LOG.debug('New client connected from %s:%d' % source)
            p=protocol.Client(sessions,names,boards,users)
            p_uri = daemon.register(p)
            LOG.debug('New URI: %s' % str(p_uri))
            users.append(p)
            client_socket.sendall(str(p_uri))	#Change as required by service discovery
            client_socket=None
        except KeyboardInterrupt as e:
            LOG.debug('Ctrl+C issued ...')
            LOG.info('Terminating server ...')
            __server_socket.close()
            break

    # If we were interrupted, make sure client socket is also closed
    if client_socket != None:
        protocol.disconnect_client(client_socket)

    # Close server socket
    __server_socket.close()
    LOG.debug('Server socket closed')
    exit(0)

#server_main('') #remove in final version ;)
# Handle Pyro Daemon running in other thread
class URIhandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.d = Pyro4.Daemon()
    def run(self):
        self.d.requestLoop()
    def register(self, cl):
        return self.d.register(cl)


class BroadcastHandler(threading.Thread):
    def __init__(self, sock_address):
        threading.Thread.__init__(self)
        self.sock_address = sock_address

    def run(self):
        self.advertise_loop()

    def advertise_loop(self):
        # Will be sending information with server's address..
        REQ = WHOISHERE + ":" + ('%s:%d' % self.sock_address)
        mc_ip, mc_port = MC_IP, MC_PORT
        mc_addr = (mc_ip, mc_port)
        ttl = 1
        try:
            while True:
                try:
                    # Here we use temporal socket
                    # as it is for multicast sending it will be not bound anyway
                    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
                    LOG.debug('UDP socket declared ...')
                    # Enable loop-back multi-cast
                    s.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
                    LOG.debug('Enabled loop-back multi-casts ...')
                    if s.getsockopt(IPPROTO_IP, IP_MULTICAST_TTL) != ttl:
                        s.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
                        LOG.debug('Set multicast TTL to %d' % ttl)
                    s.sendto(REQ, mc_addr)
                    LOG.debug('Multicast sent to [%s:%d]: %s' % (mc_addr + (REQ,)))
                    sock_addr = s.getsockname()
                    s.close()
                    LOG.debug('Closed multicast sending socket %s:%d' % sock_addr)
                    # Wait 3 seconds before sending again
                    time.sleep(5)
                except Exception as e:
                    LOG.warn('Can not send MC request: %s' % str(e))
        except KeyboardInterrupt as e:
            LOG.warn("Interrupt from keyboard. Quitting")
            return