import socket as skt
import pickle as pk
from filechunk import CHUNK_SIZE
from message import Message
import message
import sys

class Node:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        self.id = hash((host, port)) % sys.maxsize
        self.prev = None
        self.next = None
    
    def listen(self):
        s = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f'Conectado a {addr}')
                while True:
                    msg_data = conn.recv(1024)
                    if not msg_data: # Finalizou a conexão
                        break 
                    
                    msg: Message = pk.loads(msg_data)
                    if msg.type == message.NEW_NODE:
                        if self.prev == None: # `self` é a raíz da DHT
                            self.prev = self.next = addr
                        else: # Caso geral
                            new_id = hash(addr) % sys.maxsize
                            if new_id == self.id:
                                pass # TODO: Tratamento de colisões
                            dist_direct = abs(new_id - self.id) # Distância sem passar pela origem
                            dist_wrapped = sys.maxsize - new_id + self.id # Distância passando pela origem
                            if dist_direct <= dist_wrapped:
                                if new_id < self.id: # prev
                                    pass # TODO
                                else: # next
                                    pass # TODO
                            else:
                                if new_id > self.id: # prev
                                    pass # TODO
                                else: # next
                                    pass # TODO


                    conn.sendall(pk.dumps(Message(message.OK, '')))