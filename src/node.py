import socket as skt
import pickle as pk
from message import Message, ChunkMessage
import message
import sys
from filechunk import CHUNK_SIZE, convert_filename

def get_node_id(addr: tuple[str, int]) -> int:
    ip1, ip2, ip3, ip4 = addr[0].split('.')
    addr_conv = (int(ip1), int(ip2), int(ip3), int(ip4), addr[1])
    return hash(addr_conv) % sys.maxsize

def get_chunk_id(chunk: tuple[str, int]) -> int:
    filename, idx = chunk
    chunk_conv = (convert_filename(filename), idx)
    return hash(chunk_conv) % sys.maxsize

def get_distances(target_id: int, current_id: int) -> tuple[int, int]:
    dist_direct = abs(target_id - current_id) # Distância sem passar pela origem
    if target_id > current_id: # Distância passando pela origem
        dist_warped = sys.maxsize - target_id + current_id # Sentido horário
    else:
        dist_warped = sys.maxsize + target_id - current_id # Sentido anti-horário
    return dist_direct, dist_warped

class Node:
    def __init__(self, addr: tuple):
        self.addr = addr
        self.id = get_node_id(addr)
        self.prev = None
        self.next = None
        self.alive = True
        self.dict = {} # Cada entrada deve ter o formato (chunk, idx : int, final : bool)

    def __node_to_key(self, key_id: int) -> tuple[int, int, int]:
        prev_id = get_node_id(self.prev)
        next_id = get_node_id(self.next)
        dist_direct, dist_warped = get_distances(key_id, self.id)
        self_dist = min(dist_direct, dist_warped)
        dist_direct, dist_warped = get_distances(key_id, prev_id)
        prev_dist = min(dist_direct, dist_warped)
        dist_direct, dist_warped = get_distances(key_id, next_id)
        next_dist = min(dist_direct, dist_warped)
        return self_dist, prev_dist, next_dist

    # Atalhos para mandar mensagem a um nó
    def __respond_ok_message(self, s):
        s.sendall(pk.dumps(message.ok(self.addr)))
    def __send_new_node_message(self, s, addr: tuple):
        s.sendall(pk.dumps(message.new_node(addr, self.addr)))
    def __send_move_in_message(self, s, prev: tuple, next: tuple):
        s.sendall(pk.dumps(message.move_in(prev, next, self.addr)))
    def __send_up_pair_message(self, s):
        s.sendall(pk.dumps(message.up_pair(self.addr)))
    def __respond_up_next_message(self, s, next: tuple):
        s.sendall(pk.dumps(message.up_next(next, self.addr)))
    def __respond_up_prev_message(self, s, prev: tuple):
        s.sendall(pk.dumps(message.up_prev(prev, self.addr)))
    def __respond_file_found(self, s, current_msg: Message):
        s.sendall(pk.dumps(message.file_found(current_msg, self.addr)))
    def __respond_file_not_found(self, s, closest: tuple[str, int], current_msg: Message):
        s.sendall(pk.dumps(message.file_not_found(current_msg, closest, self.addr)))
    
    def __echo(self, addr: tuple):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(self.next)
            s.sendall(pk.dumps(message.echo(addr, self.addr)))
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK ## Útil para debug
    def echo(self):
        self.__echo(self.addr)
    def find(self, filename: str, idx: int):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(self.addr)
            s.sendall(pk.dumps(message.find_file((filename, idx), self.addr)))
            file_response = s.recv(1024)
            msg: Message = pk.loads(file_response)
            print(msg.type == message.FILE_FOUND)

    def enter_dht(self, known_node: tuple):
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(known_node)
            self.__send_new_node_message(s, self.addr)
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK

    # TODO: Diminuir o número de casos específicos dos if's
    def __handle_message(self, msg: Message, clSocket):
        if msg.type == message.ECHO:
            ip, port = msg.content.split(':')
            addr = (ip, int(port))
            if self.addr != addr: # Se o endereço atual for o mesmo do original, a mensagem propagou pela rede toda
                self.__echo(addr)
        
        elif msg.type == message.MOVE_IN:
            prev_ip, prev_port, next_ip, next_port = msg.content.split(':')
            self.prev = (prev_ip, int(prev_port))
            self.next = (next_ip, int(next_port))
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
                new_id = get_node_id(addr)
                if new_id == self.id:
                    self.__respond_ok_message(clSocket)
                    return # TODO: Tratamento de colisões
                dist_direct, dist_warped = get_distances(new_id, self.id)
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    is_between_prev = (new_id < self.id) if dist_direct <= dist_warped else (new_id > self.id)
                    if is_between_prev:
                        if msg.sender == self.prev: # Propagação quer voltar para prev (i.e. `key_id` está entre os dois nós)
                            s.connect(addr)
                            self.__send_move_in_message(s, self.prev, self.addr)
                            self.prev = addr # Novo nó agora é predecessor do atual
                            self.__respond_up_next_message(clSocket, addr)
                        else:
                            s.connect(self.prev)
                            self.__send_new_node_message(s, addr)
                    else: # está entre next e o nó atual
                        if msg.sender == self.next: # Propagação quer voltar para next (i.e. `key_id` está entre os dois nós)
                            s.connect(addr)
                            self.__send_move_in_message(s, self.addr, self.next) # `new_id` está entre `self.id` e `next_id`
                            self.next = addr # Novo nó agora é sucessor do atual
                            self.__respond_up_prev_message(clSocket, addr)
                        else: # Continue propagando a mensagem para frente
                            s.connect(self.next)
                            self.__send_new_node_message(s, addr)
                    response_msg_data = s.recv(1024)
                    response_msg: Message = pk.loads(response_msg_data)
                    if response_msg.type == message.UP_NEXT:
                        # substitui o nó sucessor atual pelo nó adicionado na rede
                        next_ip, next_port = response_msg.content.split(':')
                        self.next = (next_ip, int(next_port))
                    elif response_msg.type == message.UP_PREV:
                        # substitui o nó anterior atual pelo nó adicionado na rede
                        prev_ip, prev_port = response_msg.content.split(':')
                        self.prev = (prev_ip, int(prev_port))
                    else:
                        assert response_msg.type == message.OK ## Útil para debug
        elif msg.type == message.FIND_FILE:
            filename, index = msg.content.split(':')
            key = (filename, int(index))
            if key in self.dict.keys():
                # responde o clSocket com o valor
                self.__respond_file_found(clSocket, msg)
            else:
                key_id = get_chunk_id(key)
                dist_direct, dist_warped = get_distances(key_id, self.id)
                is_between_prev = (key_id < self.id) if dist_direct <= dist_warped else (key_id > self.id)
                if is_between_prev:
                    if msg.sender == self.prev: # Propagação quer voltar para prev (i.e. `key_id` está entre os dois nós)
                        self_dist, prev_dist, _ = self.__node_to_key(key_id)
                        closest = self.addr if self_dist <= prev_dist else self.next
                        self.__respond_file_not_found(clSocket, closest, msg)
                        return
                else:
                    if msg.sender == self.next: # Propagação quer voltar para next (i.e. `key_id` está entre os dois nós)
                        self_dist, _, next_dist = self.__node_to_key(key_id)
                        closest = self.addr if self_dist <= next_dist else self.next
                        self.__respond_file_not_found(clSocket, closest, msg)
                        return
                msg.sender = self.addr
                with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                    if is_between_prev:
                        s.connect(self.prev) # Propague para trás
                    else:
                        s.connect(self.next) # Propague para frente
                    s.sendall(pk.dumps(msg))
                    response_msg_data = s.recv(1024)
                    clSocket.sendall(response_msg_data) # Repasse a resposta recebida
            return
        elif msg.type == message.PUT_FILE:
            self.__respond_ok_message(clSocket)
            response_msg_data = b''
            while True: # Recebe ChunkMessage em pedaços
                suffix_data = clSocket.recv(4096)
                if not suffix_data:
                    break
                response_msg_data += suffix_data
            response_msg: ChunkMessage = pk.loads(response_msg_data)
            key_id = get_chunk_id(response_msg.key)
            self_dist, prev_dist, next_dist = self.__node_to_key(key_id)
            if self_dist <= prev_dist and self_dist <= next_dist:
                self.dict[response_msg.key] = response_msg.raw
            return
        
        self.__respond_ok_message(clSocket)
                    

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
                        print(f'{msg.sender} enviou {len(msg_data)} bytes para {self.addr}')
                        self.__handle_message(msg, conn)
