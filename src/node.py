import socket as skt
import pickle as pk
from filechunk import CHUNK_SIZE
from message import Message
import message

class Node:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        self.id = hash((host, port))
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
                            prev_id = hash(self.prev)
                            next_id = hash(self.next)
                            dist_prev = abs(self.id - prev_id)
                            dist_next = abs(self.id - next_id)
                            # TODO
                    conn.sendall(message.OK)