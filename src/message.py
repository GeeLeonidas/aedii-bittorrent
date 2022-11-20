# Tipos de mensagem
OK              = b'\x00'
NEW_NODE        = b'\x01'
MOVE_IN         = b'\x02'
UP_NEXT         = b'\x03'
UP_PREV         = b'\x04'
UP_PAIR         = b'\x05' # Para quando a DHT possui apenas um par de nós
ECHO            = b'\x06'
FIND_FILE       = b'\x07'
FILE_FOUND      = b'\x08'
FILE_NOT_FOUND  = b'\x09'
PUT_FILE        = b'\x0A'

class Message:
    def __init__(self, type: bytes, content: str, sender: tuple):
        assert len(type) == len(OK)
        self.type = type
        self.content = content
        self.sender = sender # Precisa ser aqui, pois o `addr` da conexão possui uma porta aleatória

def ok(sender: tuple):
    return Message(OK, '', sender)

def new_node(addr: tuple, sender: tuple):
    return Message(NEW_NODE, f'{addr[0]}:{addr[1]}', sender)

def move_in(prev: tuple, next: tuple, sender: tuple):
    return Message(MOVE_IN, f'{prev[0]}:{prev[1]}:{next[0]}:{next[1]}', sender)

def up_next(next: tuple, sender: tuple):
    return Message(UP_NEXT, f'{next[0]}:{next[1]}', sender)

def up_prev(prev: tuple, sender: tuple):
    return Message(UP_PREV, f'{prev[0]}:{prev[1]}', sender)

def up_pair(sender: tuple):
    return Message(UP_PAIR, '', sender)

def echo(addr: tuple, sender: tuple):
    return Message(ECHO, f'{addr[0]}:{addr[1]}', sender)

def find_file(filename: str, idx: int, sender: tuple):
    return Message(FIND_FILE, f'{filename}:{idx}', sender)

def file_found(current_msg: Message, sender: tuple):
    assert current_msg.type == FIND_FILE
    return Message(FILE_FOUND, f'{sender[0]}:{sender[1]}', sender)

def file_not_found(current_msg: Message, sender: tuple):
    assert current_msg.type == FIND_FILE
    return Message(FILE_NOT_FOUND, '', sender)

def put_file(filename: str, idx: int, chunk: bytes, final: bool, sender: tuple):
    return Message(PUT_FILE, f'{filename}:{idx}:{chunk}:{final}', sender)