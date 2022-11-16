import socket as skt
import threading as thd
import mensagem as msg
import time
import pickle

HOST = 'localhost'
PORT = 12345

## create a tcp socket that listens for incoming connections
def listen():
    s = skt.socket(skt.AF_INET)
    s.bind((HOST, PORT))
    s.listen()
    print ('Escutando')
    while True:
        conn, addr = s.accept()
        
        ## receive message
        data = conn.recv(1024)
        data_string = pickle.loads(data)
        print('Message received')
        print(data_string)

## send a message to a peer
def send_request(mensagem : msg.mensagem, ip : str, port : int):
    s = skt.socket(skt.AF_INET)
    s.connect((ip, port))
    data_string = pickle.dumps(mensagem)
    s.send(data_string)
    print('Message sent')
    s.close()


## create a message and send it to a peer
def send_test(ip : str, port : int):
    m = msg.mensagem('TEST', skt.gethostbyname(skt.gethostname()), PORT, 'BELA CHAVE')
    m.chave = input('Digite a chave: ') ## input message text (for testing)
    send_request(m, ip, port)




    
        
