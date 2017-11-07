import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
LOG = logging.getLogger()
# Imports----------------------------------------------------------------------
from application.common import \
    __RSP_BADFORMAT, __RSP_OK, __RSP_UNAME_TAKEN, __RSP_SESSION_ENDED, __RSP_SESSION_TAKEN, __RSP_UNKNCONTROL, \
    __REQ_UNAME, __REQ_GET_SESS, __REQ_JOIN_SESS, __REQ_NEW_SESS, \
    __MSG_FIELD_SEP, __MSG_SEP,\
    TCP_RECEIVE_BUFFER_SIZE

from threading import Thread, Lock
from socket import AF_INET, SOCK_STREAM, socket, SHUT_RD
from socket import error as soc_err
from base64 import decodestring, encodestring
from time import asctime,localtime

def handle_user_input(myclient):
    logging.info( 'Starting input processor' )

    while 1:
        logging.info('\nHit Enter to init user-input ...')
        raw_input('')
        # get sessions and display
        myclient.get_sess()

        logging.info('\nEnter number of session to join or \n Q to create new session or \n E to exit : ')
        m = raw_input('')
        if len(m) <= 0:
            continue
        elif m == 'E':
            myclient.stop()
            return
        elif m == 'Q':
            myclient.create_sess()
        else:
            myclient.join_sess(m)

def serialize(msg):
    return encodestring(msg)

def deserialize(msg):
    return decodestring(msg)

class Client():

    def __init__(self):
        self.__send_lock = Lock()
        self.__on_recv = None

    def stop(self):
        self.__s.shutdown(SHUT_RD)
        self.__s.close()

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

    def get_sess(self):
        req = __REQ_GET_SESS + __MSG_FIELD_SEP
        return self.__session_send(req)

    def create_sess(self):
        req = __REQ_NEW_SESS + __MSG_FIELD_SEP
        return self.__session_send(req)

    def join_sess(self, msg):
        data = serialize(msg)
        req = __REQ_JOIN_SESS + __MSG_FIELD_SEP + data
        return self.__session_send(req)


    def __session_send(self, msg):
        m = msg + __MSG_SEP
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
            return r

    def __session_rcv(self):
        m,b = '',''
        try:
            b = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)
            m += b
            while len(b) > 0 and not (b.endswith(__MSG_SEP)):
                b = self.__s.recv(TCP_RECEIVE_BUFFER_SIZE)
                m += b
            if len(b) <= 0:
                logging.debug( 'Socket receive interrupted'  )
                self.__s.close()
                m = ''
            m = m[:-1]
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

    def __protocol_rcv(self,message):
        logging.debug('Received [%d bytes] in total' % len(message))
        if len(message) < 2:
            logging.debug('Not enough data received from %s ' % message)
            return
        logging.debug('Response control code (%s)' % message[0])
        if message.startswith(__RSP_OK + __MSG_FIELD_SEP):
            logging.debug('Server confirmed message was published')
            self.__on_published()
        # TODO: notify
        elif message.startswith(RSP_NOTIFY + __MSG_FIELD_SEP):
            logging.debug('Server notification received, fetching messages')
            self.__fetch_msgs()
        elif message.startswith(__RSP_OK + __MSG_FIELD_SEP):
            logging.debug('Messages retrieved ...')
            msgs = message[2:].split(__MSG_FIELD_SEP)
            msgs = map(deserialize,msgs)
            for m in msgs:
                self.__on_recv(m)
        else:
            logging.debug('Unknown control message received: %s ' % message)
            return __RSP_UNKNCONTROL

    def loop(self):
        logging.info('Falling to receiver loop ...')
        #self.__fetch_msgs()
        while 1:
            m = self.__session_rcv()
            if len(m) <= 0:
                break
            self.__protocol_rcv(m)

if __name__ == '__main__':
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

    if c.connect(('127.0.0.1',7777)):

        t = Thread(name='InputProcessor',\
                   target=handle_user_input, args=(c,))
        t.start()

        c.loop()
        t.join()

    logging.info('Terminating')