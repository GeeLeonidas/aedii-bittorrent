# Tipos de mensagem
OK          = b'\x00'
NEW_NODE    = b'\x01'
MOVE_IN     = b'\x02'
UP_NEXT     = b'\x03'
UP_PREV     = b'\x04'
UP_PAIR     = b'\x05' # Para quando a DHT possui apenas um par de nós
ECHO        = b'\x06'
GET_FILE    = b'\x07'

class Message:
    def __init__(self, type: bytes, content: str, sender: tuple):
        assert len(type) == len(OK)
        self.type = type
        self.content = content
        self.sender = sender # Precisa ser aqui, pois o `addr` da conexão possui uma porta aleatória

def ok_message(sender: tuple):
    return Message(OK, '', sender)

def new_node_message(addr: tuple, sender: tuple):
    return Message(NEW_NODE, f'{addr[0]}:{addr[1]}', sender)

def move_in_message(prev: tuple, next: tuple, sender: tuple):
    return Message(MOVE_IN, f'{prev[0]}:{prev[1]}:{next[0]}:{next[1]}', sender)

def up_next_message(next: tuple, sender: tuple):
    return Message(UP_NEXT, f'{next[0]}:{next[1]}', sender)

def up_prev_message(prev: tuple, sender: tuple):
    return Message(UP_PREV, f'{prev[0]}:{prev[1]}', sender)

def up_pair_message(sender: tuple):
    return Message(UP_PAIR, '', sender)

def echo_message(addr: tuple, sender: tuple):
    return Message(ECHO, f'{addr[0]}:{addr[1]}', sender)

def get_file_message(filename: str, idx: int):
    return Message(GET_FILE, f'{filename}:{idx}', '')

def get_file_response(content: tuple, sender: tuple):
    return Message(GET_FILE, content, sender) # content deve ter o formato (chunk, idx, final)