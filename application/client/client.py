# Setup Python logging --------------------------------------------------------
import logging
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
    RSP_OK, RSP_UNKNCONTROL, \
    REQ_UNAME, REQ_GET_SESS, REQ_JOIN_SESS, REQ_NEW_SESS, REQ_GUESS, PUSH_END_SESSION,\
    MSG_FIELD_SEP, MSG_SEP, REQ_QUIT_SESS, END_TERM


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


    def set_on_recv_callback(self,on_recv_f):
        '''
        Sets on_recv funtion
        '''
        self.__on_recv = on_recv_f

    def connect(self,srv_addr):
        '''
         Connect to the server socket
        @param: srv_addr:
        '''
        self.__s = socket(AF_INET,SOCK_STREAM)
        try:
            self.__s.connect(srv_addr)
            logging.info('Connected to server at %s:%d' % srv_addr)
            s_uri = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)	#get Pyro4 URI
            self.server = Pyro4.Proxy(s_uri)
            return True
        except soc_err as e:
            logging.error('Can not connect to server at %s:%d'\
                      ' %s ' % (srv_addr+(str(e),)))
        return False

    def send_username(self, username):
        '''
        Send request to the server to check username
        @param: username: username wanted to choose
        '''
        return self.server.chooseName(username)

    def get_sess(self):
        '''
        Send request to retrieve sessions list
        '''
        return self.server.getSessions()

    def create_sess(self, msg):
        '''
        Send request to the server to create new session
        @param: msg: number of desired players and the name of the session we want to create
        '''
        return self.server.newSession(msg)

    def join_sess(self, msg):
        '''
        Send request to the server to join a session
        @param: msg: session name to join
        '''
        return self.server.joinSession(msg)

    def send_guess(self, msg):
        '''
        Send request to the server to check the guessed number
        @param: msg: entered number and its coordinates
        '''
        data = msg
        req = REQ_GUESS + MSG_FIELD_SEP + data
        return self.__session_send(req)

    def exit_game(self):
        '''
        Send request to the server to exit from session
        '''
        req = REQ_QUIT_SESS + MSG_FIELD_SEP
        return self.__session_send(req)

    def __session_send(self, msg):
        '''
        Send data to the server
        @param: msg: message to send with request code
        '''
        m = msg + END_TERM
        with self.__send_lock:
            r = False
            try:
                self.__s.sendall(m)
                r = True
            except KeyboardInterrupt:
                self.__s.close()
                logging.info('Ctrl+C issued, terminating ...')
            except soc_err as e:
                if e.errno == 107:
                    logging.warn('Server closed connection, terminating ...')
                else:
                    logging.error('Connection error: %s' % str(e))
                self.__s.close()
                logging.info('Disconnected')
            logging.info('Send: [ %s ]' % m)
            return r

    def __session_rcv(self):
        '''
        Receive data from the server
        @returns: message received from the server
        '''
        m,b = [],''
        try:
            b = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)

            # while len(b) > 0 and not (b.endswith(MSG_SEP)):
            #     b = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)
            #     m += b
            if len(b) <= 0:
                logging.debug( 'Socket receive interrupted'  )
                self.__s.close()
                m = []
            if len(b) > 0:
                m = b.split(END_TERM)[:-1]

        except KeyboardInterrupt:
            self.__s.close()
            logging.info( 'Ctrl+C issued, terminating ...' )
            m = []
        except soc_err as e:
            if e.errno == 107:
                logging.warn( 'Server closed connection, terminating ...' )
            else:
                logging.error( 'Connection error: %s' % str(e) )
            self.__s.close()
            logging.info( 'Disconnected' )
            m = []
            raise soc_err
        return m

    def loop(self, q):
        '''
        Create infinite loop to listen to the server
        @param: q: queue to put received messages in
        '''
        logging.info('Falling to receiver loop ...')
        try:
            while 1:
                sleep(1)
                msgs = self.__session_rcv()
                for m in msgs:
                    if len(m) <= 0:
                        break
                    logging.info('Received [%d bytes] in total' % len(m))
                    logging.info('Received message %s' % m)
                    q.put(m)

        except soc_err as e:
            logging.info("Socket has died")


        except KeyboardInterrupt:
            self.__s.close()
            exit(0)


def main():
    '''
    Runs the client side of the application
    '''
    def on_recv(msg):
        '''
        Logs received messages
        @param: msg:
        '''
        if len(msg) > 0:
            msg = msg.split(' ')
            msg = tuple(msg[:3]+[' '.join(msg[3:])])
            t_form = lambda x: asctime(localtime(float(x)))
            m_form = lambda x: '%s [%s:%s] -> '\
                        '%s' % (t_form(x[0]),x[1],x[2],x[3].decode('utf-8'))
            m = m_form(msg)
            logging.info('\n%s' % m)

    c = Client() # Create the Client object
    c.set_on_recv_callback(on_recv)
    logging.info( 'Starting input processor' )
    app = Application(c) # Create main gui object
    app.mainloop() # Start gui object

    # Join thread before terminating
    for t in app.threads:
        t.join()

    logging.info('Terminating')


if __name__ == "__main__":
    main()
