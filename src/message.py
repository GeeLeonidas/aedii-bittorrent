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
GET_FILE        = b'\x0B'

class Message:
    def __init__(self, type: bytes, content: str, sender: tuple[str, int]):
        assert len(type) == len(OK)
        self.type = type
        self.content = content
        self.sender = sender # Precisa ser aqui, pois o `addr` da conexão possui uma porta aleatória

class ChunkMessage:
    def __init__(self, key: tuple[str, int], raw: bytes):
        self.key = key
        self.raw = raw

def ok(sender: tuple[str, int]):
    return Message(OK, '', sender)

def new_node(addr: tuple[str, int], sender: tuple[str, int]):
    return Message(NEW_NODE, f'{addr[0]}:{addr[1]}', sender)

def move_in(prev: tuple[str, int], next: tuple[str, int], sender: tuple[str, int]):
    return Message(MOVE_IN, f'{prev[0]}:{prev[1]}:{next[0]}:{next[1]}', sender)

def up_next(next: tuple[str, int], sender: tuple[str, int]):
    return Message(UP_NEXT, f'{next[0]}:{next[1]}', sender)

def up_prev(prev: tuple[str, int], sender: tuple[str, int]):
    return Message(UP_PREV, f'{prev[0]}:{prev[1]}', sender)

def up_pair(sender: tuple[str, int]):
    return Message(UP_PAIR, '', sender)

def echo(addr: tuple[str, int], sender: tuple[str, int]):
    return Message(ECHO, f'{addr[0]}:{addr[1]}', sender)

def find_file(key: tuple[str, int], sender: tuple[str, int]): # key = (filename, idx)
    return Message(FIND_FILE, f'{key[0]}:{key[1]}', sender)

def file_found(current_msg: Message, sender: tuple[str, int]):
    assert current_msg.type == FIND_FILE
    return Message(FILE_FOUND, f'{sender[0]}:{sender[1]}', sender)

def file_not_found(current_msg: Message, closest: tuple[str, int], sender: tuple[str, int]):
    assert current_msg.type == FIND_FILE
    return Message(FILE_NOT_FOUND, f'{closest[0]}:{closest[1]}', sender)

def put_file(sender: tuple[str, int]):
    return Message(PUT_FILE, '', sender)

def get_file(sender: tuple[str, int], key): # key = (filename, idx)
    return Message(GET_FILE, f'{key[0]}:{key[1]}', sender)