# Setup Python logging --------------------------------------------------------
import logging
import Pyro4
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from application.client.client_gui import Application
from threading import Lock
from socket import AF_INET, SOCK_STREAM, socket, SHUT_RD
from socket import error as soc_err
from base64 import decodestring, encodestring
from time import asctime,localtime,sleep
from application.common import TCP_RECEIVE_BUFFER_SIZE, \
     END_TERM

#@Pyro4.expose
class Client():
    '''
        Client class that handles client server communication.
    '''

    def __init__(self):
        self.__send_lock = Lock()
        self.__on_recv = None


    def stop(self):
        '''
         closes the client socket
        '''
        self.__s.shutdown(SHUT_RD)
        self.__s.close()

    def connect(self,srv_addr):
        '''
        Connect to the server socket and gets remote object
        @param: srv_addr:
        '''
        self.__s = socket(AF_INET,SOCK_STREAM)
        try:
            self.__s.connect(srv_addr)
            logging.info('Connected to server at %s:%d' % srv_addr)
            s_uri = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)	#get Pyro4 URI
            LOG.info('Got client manager %s' % str(s_uri))
            self.server = Pyro4.Proxy(s_uri)
            self.__s.close()
            return True
        except soc_err as e:
            logging.error('Can not connect to server at %s:%d'\
                      ' %s ' % (srv_addr+(str(e),)))
        return False

    def register_gate(self, gate):
        '''
        Calles the server function to register the client gate
        @param: gate: client gate
        '''
        self.server.register(gate)

    def send_username(self, username):
        '''
        Calles the server function to check username
        @param: username: username wanted to choose
        '''
        return self.server.chooseName(username)

    def get_sess(self):
        '''
        Calles the server function to retrieve sessions list
        '''
        return self.server.getSessions()

    def create_sess(self, msg):
        '''
        Calles the server function to create new session
        @param: msg: number of desired players and the name of the session we want to create
        '''
        return self.server.newSession(msg)

    def join_sess(self, msg):
        '''
        Calles the server function to join a session
        @param: msg: session name to join
        '''
        return self.server.joinSession(msg)

    def send_guess(self, msg):
        '''
        Calles the server function to check the guessed number
        @param: msg: entered number and its coordinates
        '''
        return self.server.sendGuess(msg)

    def exit_game(self, msg):
        '''
        Calles the server function to exit from session
        '''
        return self.server.leave(msg)


def main():
    '''
    Runs the client side of the application
    '''
    c = Client() # Create the Client object
    logging.info( 'Starting input processor' )
    app = Application(c) # Create main gui object
    app.mainloop() # Start gui object

    # Join thread before terminating
    for t in app.threads:
        t.join()

    logging.info('Terminating')


if __name__ == "__main__":
    main()
