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
    MSG_FIELD_SEP, MSG_SEP, REQ_QUIT_SESS \

#Client class that handles client and server communication
class Client():

    def __init__(self):
        self.__send_lock = Lock()
        self.__on_recv = None

    # closes the client socket
    def stop(self):
        self.__s.shutdown(SHUT_RD)
        self.__s.close()

    # logs mag
    def set_on_recv_callback(self,on_recv_f):
        self.__on_recv = on_recv_f

    def connect(self,srv_addr):
        self.__s = socket(AF_INET,SOCK_STREAM)
        try:
            self.__s.connect(srv_addr)
            logging.info('Connected to server at %s:%d' % srv_addr)
            return True
        except soc_err as e:
            logging.error('Can not connect to server at %s:%d'\
                      ' %s ' % (srv_addr+(str(e),)))
        return False

    def send_username(self, username):
        data = username
        req = REQ_UNAME + MSG_FIELD_SEP + data
        return self.__session_send(req)

    def get_sess(self):
        req = REQ_GET_SESS + MSG_FIELD_SEP
        return self.__session_send(req)

    def create_sess(self, msg):
        data = msg
        req = REQ_NEW_SESS + MSG_FIELD_SEP+ data
        return self.__session_send(req)

    def join_sess(self, msg):
        data = msg
        req = REQ_JOIN_SESS + MSG_FIELD_SEP + data
        return self.__session_send(req)

    def send_guess(self, msg):
        data = msg
        req = REQ_GUESS + MSG_FIELD_SEP + data
        return self.__session_send(req)

    def exit_game(self):
        req = REQ_QUIT_SESS + MSG_FIELD_SEP
        return self.__session_send(req)

    def __session_send(self, msg):
        m = msg# + MSG_SEP
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
        m,b = '',''
        try:
            b = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)
            m += b
            # while len(b) > 0 and not (b.endswith(MSG_SEP)):
            #     b = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)
            #     m += b
            if len(b) <= 0:
                logging.debug( 'Socket receive interrupted'  )
                self.__s.close()
                m = ''
        except KeyboardInterrupt:
            self.__s.close()
            logging.info( 'Ctrl+C issued, terminating ...' )
            m = ''
        except soc_err as e:
            if e.errno == 107:
                logging.warn( 'Server closed connection, terminating ...' )
            else:
                logging.error( 'Connection error: %s' % str(e) )
            self.__s.close()
            logging.info( 'Disconnected' )
            m = ''
        return m

    def loop(self, q):
        logging.info('Falling to receiver loop ...')
        try:
            while 1:
                sleep(1)
            # q.put("sessions")
                m = self.__session_rcv()
                if len(m) <= 0:
                    break
                logging.info('Received [%d bytes] in total' % len(m))
                logging.info('received message %s' % m)
                q.put(m)
            #    self.__protocol_rcv(m)

        except KeyboardInterrupt:
            self.__s.close()
            exit(0)


def main():
    def on_recv(msg):
        if len(msg) > 0:
            msg = msg.split(' ')
            msg = tuple(msg[:3]+[' '.join(msg[3:])])
            t_form = lambda x: asctime(localtime(float(x)))
            m_form = lambda x: '%s [%s:%s] -> '\
                        '%s' % (t_form(x[0]),x[1],x[2],x[3].decode('utf-8'))
            m = m_form(msg)
            logging.info('\n%s' % m)

    c = Client()
    c.set_on_recv_callback(on_recv)
    logging.info( 'Starting input processor' )
    app = Application(c)
    app.mainloop()


    logging.info('Terminating')



if __name__ == "__main__":
    main()
