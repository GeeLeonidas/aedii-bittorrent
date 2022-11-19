import socket as skt
import pickle as pk
from message import Message
import message
import sys

class Node:
    def __init__(self, addr: tuple):
        self.addr = addr
        self.id = hash(addr) % sys.maxsize
        self.prev = None
        self.next = None
        self.alive = True

    # Atalhos para mandar mensagem a um nó
    def __send_ok_message(self, s):
        s.sendall(pk.dumps(message.ok_message(self.addr)))
    def __send_new_node_message(self, s, addr: tuple):
        s.sendall(pk.dumps(message.new_node_message(addr, self.addr)))
    def __send_move_in_message(self, s, prev: tuple, next: tuple):
        s.sendall(pk.dumps(message.move_in_message(prev, next, self.addr)))
    def __send_up_next_message(self, s, next: tuple):
        s.sendall(pk.dumps(message.up_next_message(next, self.addr)))
    def __send_up_prev_message(self, s, prev: tuple):
        s.sendall(pk.dumps(message.up_prev_message(prev, self.addr)))

    def enter_dht(self, known_node: tuple):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(known_node)
            self.__send_new_node_message(s, self.addr)
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK

    def handle_message(self, msg: Message):
        if msg.type == message.MOVE_IN:
            prev_ip, prev_port, next_ip, next_port = msg.content.split(':')
            self.prev = (prev_ip, int(prev_port))
            self.next = (next_ip, int(next_port))
            
            with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                if msg.sender == self.next: # Foi o próximo nó que requisitou MOVE_IN
                    s.connect(self.prev)
                    self.__send_up_next_message(s, self.addr)
                else: # Foi o nó anterior que requisitou MOVE_IN
                    s.connect(self.next)
                    self.__send_up_prev_message(s, self.addr)                
                response_msg_data = s.recv(1024)
                response_msg: Message = pk.loads(response_msg_data)
                assert response_msg.type == message.OK
        elif msg.type == message.UP_NEXT:
            # substitui o nó sucessor atual pelo nó adicionado na rede
            next_ip, next_port = msg.content.split(':')
            self.next = (next_ip, int(next_port))
        elif msg.type == message.UP_PREV:
            # substitui o nó anterior atual pelo nó adicionado na rede
            prev_ip, prev_port = msg.content.split(':')
            self.prev = (prev_ip, int(prev_port))
        elif msg.type == message.NEW_NODE:
            host, port = msg.content.split(':')
            addr = (host, int(port)) # Endereço do autor original da mensagem

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
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    if dist_direct <= dist_wrapped:
                        if new_id < self.id: # prev
                            if new_id < prev_id: # Continue propagando a mensagem para trás
                                s.connect(self.prev)
                                self.__send_new_node_message(s, addr)
                            else: # `new_id` está entre `prev_id` e `self.id`
                                s.connect(addr)
                                self.__send_move_in_message(s, self.prev, self.addr)
                                self.prev = addr # Novo nó agora é predecessor do atual
                            response_msg_data = s.recv(1024)
                            response_msg: Message = pk.loads(response_msg_data)
                            assert response_msg.type == message.OK ## Útil para debug
                        else: # next
                            if new_id > next_id: # Continue propagando a mensagem para frente
                                s.connect(self.next)
                                self.__send_new_node_message(s, addr)
                            else: # `new_id` está entre `self.id` e `next_id`
                                s.connect(addr)
                                self.__send_move_in_message(s, self.addr, self.next)
                                self.next = addr # Novo nó agora é sucessor do atual
                            response_msg_data = s.recv(1024)
                            response_msg: Message = pk.loads(response_msg_data)
                            assert response_msg.type == message.OK ## Útil para debug                                
                    else:
                        if new_id > self.id: # prev
                            # Propaga para trás até passar da origem
                            s.connect(self.prev)
                        else: # next
                            # Propaga para frente até passar da origem
                            s.connect(self.next)
                        self.__send_new_node_message(s, addr)
                        response_msg_data = s.recv(1024)
                        response_msg: Message = pk.loads(response_msg_data)
                        assert response_msg.type == message.OK ## Útil para debug

    def listen(self):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.bind(self.addr)
            while self.alive:
                s.listen()
                conn, conn_addr = s.accept()
                with conn:
                    print(f'Conectado a {conn_addr}')
                    while True:
                        msg_data = conn.recv(1024)
                        if not msg_data: # Finalizou a conexão
                            break 
                        msg: Message = pk.loads(msg_data)
                        self.handle_message(msg)
                        self.__send_ok_message(conn)