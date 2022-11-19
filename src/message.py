# Tipos de mensagem
OK          = b'\x00'
NEW_NODE    = b'\x01'
MOVE_IN     = b'\x02'
UP_NEXT     = b'\x03'
UP_PREV     = b'\x04'

class Message:
    def __init__(self, type: bytes, content: str):
        assert len(type) == len(OK)
        self.type = type
        self.content = content

def ok_message():
    return Message(OK, '')

def new_node_message(addr: tuple):
    return Message(NEW_NODE, f'{addr[0]}:{addr[1]}')

def move_in_message(prev: tuple, next: tuple):
    return Message(MOVE_IN, f'{prev[0]}:{prev[1]}:{next[0]}:{next[1]}')

def up_next_message(next: tuple):
    return Message(UP_NEXT, f'{next[0]}:{next[1]}')

def up_prev_message(prev: tuple):
    return Message(UP_PREV, f'{prev[0]}:{prev[1]}')