import socket as skt
import pickle as pk
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

    def handle_message(self, sender: tuple, msg: Message):
        if msg.type == message.MOVE_IN:
            prev_id, prev_port, next_id, next_port = msg.content.split(':')
            self.prev = (prev_id, prev_port)
            self.next = (next_id, next_port)
            
            # envia mensagem up_next para o nó predecessor
            with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                s.connect((self.prev[0], self.prev[1]))
                s.sendall(pk.dumps(message.up_next_message((self.host, self.port))))
                response_msg_data = s.recv(1024)
                response_msg: Message = pk.loads(response_msg_data)
                assert response_msg.type == message.OK
        elif msg.type == message.UP_NEXT:
            # substitui o nó sucessor atual pelo nó adicionado na rede
            next_id, next_port = msg.content.split(':')
            self.next = (next_id, next_port)
        elif msg.type == message.NEW_NODE:
            host, port = msg.content.split(':')
            addr = (host, port) # Endereço do autor original da mensagem

            if self.prev == None: # `self` é a raíz da DHT
                self.prev = self.next = addr
            else: # Caso geral
                new_id = hash(addr) % sys.maxsize
                if new_id == self.id:
                    return # TODO: Tratamento de colisões
                
                dist_direct = abs(new_id - self.id) # Distância sem passar pela origem
                dist_wrapped = sys.maxsize - new_id + self.id # Distância passando pela origem

                prev_id = hash(self.prev) % sys.maxsize
                next_id = hash(self.next) % sys.maxsize
                if dist_direct <= dist_wrapped:
                    if new_id < self.id: # prev
                        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                            if new_id < prev_id: # Continue propagando a mensagem para trás
                                s.connect(self.prev)
                                s.sendall(pk.dumps(message.new_node_message(addr)))
                            else: # `new_id` está entre `prev_id` e `self.id`
                                s.connect(addr)
                                s.sendall(pk.dumps(message.move_in_message(self.prev, self.id)))
                                self.prev = addr # Novo nó agora é predecessor do atual
                            response_msg_data = s.recv(1024)
                            response_msg: Message = pk.loads(response_msg_data)
                            assert response_msg.type == message.OK ## Útil para debug
                    else: # next
                        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                            if new_id > next_id: # Continue propagando a mensagem para frente
                                s.connect(self.next)
                                s.sendall(pk.dumps(message.new_node_message(addr)))
                            else: # `new_id` está entre `self.id` e `next_id`
                                s.connect(addr)
                                s.sendall(pk.dumps(message.move_in_message(self.id, self.next)))
                                self.next = addr # Novo nó agora é sucessor do atual
                            response_msg_data = s.recv(1024)
                            response_msg: Message = pk.loads(response_msg_data)
                            assert response_msg.type == message.OK ## Útil para debug                                
                else:
                    if new_id > self.id: # prev
                        pass # TODO
                    else: # next
                        pass # TODO

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
                    self.handle_message(addr, msg)
                    conn.sendall(pk.dumps(message.ok_message()))