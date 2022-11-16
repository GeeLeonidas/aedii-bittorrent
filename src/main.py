import peers as p
import P2P as p2p
import threading as thd
import time


if __name__ == "__main__":

    ## enter port number
    p2p.PORT = int(input('Digite a porta: '))

    ## start listening thread
    t = thd.Thread(target=p2p.listen)
    t.start()

    ## enter ip and port of the peer to send a message to
    ip = input('Digite o ip do peer: ')
    port = int(input('Digite a porta do peer: '))
    p2p.send_test(ip, port)

    pass