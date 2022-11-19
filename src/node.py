import socket as skt
import pickle as pk
from message import Message
import message
import sys

def get_id(addr: tuple) -> int:
    ip1, ip2, ip3, ip4 = addr[0].split('.')
    addr_conv = (int(ip1), int(ip2), int(ip3), int(ip4), addr[1])
    return hash(addr_conv) % sys.maxsize

class Node:
    def __init__(self, addr: tuple):
        self.addr = addr
        self.id = get_id(addr)
        self.prev = None
        self.next = None
        self.alive = True
        self.dict = {}

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
    def __send_up_pair_message(self, s):
        s.sendall(pk.dumps(message.up_pair_message(self.addr)))
    
    def __echo(self, addr: tuple):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(self.next)
            s.sendall(pk.dumps(message.echo_message(addr, self.addr)))
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK ## Útil para debug
    def echo(self):
        self.__echo(self.addr)

    def enter_dht(self, known_node: tuple):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(known_node)
            self.__send_new_node_message(s, self.addr)
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK

    def __handle_message(self, msg: Message):
        if msg.type == message.ECHO:
            ip, port = msg.content.split(':')
            addr = (ip, int(port))
            if self.addr != addr: # Se o endereço atual for o mesmo do original, a mensagem propagou pela rede toda
                self.__echo(addr)
        
        elif msg.type == message.MOVE_IN:
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
        elif msg.type == message.UP_PAIR:
            self.prev = self.next = msg.sender
        elif msg.type == message.NEW_NODE:
            host, port = msg.content.split(':')
            addr = (host, int(port)) # Endereço do autor original da mensagem

            if self.prev == None: # `self` é a raíz da DHT
                self.prev = self.next = addr
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    s.connect(addr) # Dizer para o novo nó como se atualizar
                    self.__send_up_pair_message(s)
                    response_msg_data = s.recv(1024)
                    response_msg: Message = pk.loads(response_msg_data)
                    assert response_msg.type == message.OK ## Útil para debug
            else: # Caso geral
                new_id = get_id(addr)
                if new_id == self.id:
                    return # TODO: Tratamento de colisões
                
                dist_direct = abs(new_id - self.id) # Distância sem passar pela origem
                if new_id > self.id: # Distância passando pela origem
                    dist_warped = sys.maxsize - new_id + self.id # Sentido horário
                else:
                    dist_warped = sys.maxsize + new_id - self.id # Sentido anti-horário

                prev_id = get_id(self.prev)
                next_id = get_id(self.next)
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    if dist_direct <= dist_warped:
                        if new_id < self.id: # prev
                            if new_id > prev_id or (new_id < prev_id and prev_id > self.id) or prev_id == next_id:
                                s.connect(addr)
                                self.__send_move_in_message(s, self.prev, self.addr) # `new_id` está entre `prev_id` e `self.id`
                                self.prev = addr # Novo nó agora é predecessor do atual
                            else:
                                s.connect(self.prev)
                                self.__send_new_node_message(s, addr)
                        else: # next
                            if new_id < next_id or (new_id > next_id and next_id < self.id) or prev_id == next_id:
                                s.connect(addr)
                                self.__send_move_in_message(s, self.addr, self.next) # `new_id` está entre `self.id` e `next_id`
                                self.next = addr # Novo nó agora é sucessor do atual
                            else: # Continue propagando a mensagem para frente
                                s.connect(self.next)
                                self.__send_new_node_message(s, addr)                      
                    else:
                        if new_id > self.id: # prev
                            if new_id > prev_id or prev_id == next_id: # `new_id` está entre `prev_id` e `self.id`
                                s.connect(addr)
                                self.__send_move_in_message(s, self.prev, self.addr)
                                self.prev = addr # Novo nó agora é predecessor do atual
                            else: # Propaga para trás até passar da origem
                                s.connect(self.prev)
                                self.__send_new_node_message(s, addr)
                        else: # next
                            if new_id < next_id or prev_id == next_id: # `new_id` está entre `self.id` e `prev_id`
                                s.connect(addr)
                                self.__send_move_in_message(s, self.addr, self.next)
                                self.next = addr # Novo nó agora é sucessor do atual
                            else: # Propaga para frente até passar da origem
                                s.connect(self.next)
                                self.__send_new_node_message(s, addr)
                    response_msg_data = s.recv(1024)
                    response_msg: Message = pk.loads(response_msg_data)
                    assert response_msg.type == message.OK ## Útil para debug
        elif msg.type == message.get_file_message:
            key = str(msg.content)
            if key in self.dict:
                # responde o clSocket com o valor
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    response_msg: Message = message.get_file_response(self.dict[key], self.addr)
                    clSocket.sendall(pk.dumps(response_msg))
            else:
                # repassa a mensagem para o próximo nó
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    s.connect(self.next)
                    s.sendall(pk.dumps(msg))
                    response_msg_data = s.recv(1024)
                    response_msg: Message = pk.loads(response_msg_data)
                    clSocket.sendall(pk.dumps(response_msg))        
        if(msg.type != message.get_file_message):
            self.__send_ok_message(clSocket)
                    

    def listen(self):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.bind(self.addr)
            s.listen()
            s.settimeout(1) # Adiciona um delay (em seg.) para ele verificar se `self.alive` é verdadeiro
            while self.alive:
                try:
                    conn, conn_addr = s.accept()
                except TimeoutError:
                    continue
                with conn:
                    while True:
                        msg_data = conn.recv(1024)
                        if not msg_data: # Finalizou a conexão
                            break
                        msg: Message = pk.loads(msg_data)
                        print(f'{msg.sender} enviou mensagem para {self.addr}')
                        self.__handle_message(msg)
