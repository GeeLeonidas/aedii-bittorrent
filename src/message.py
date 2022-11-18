# Tipos de mensagem
OK          = b'\x00'
NEW_NODE    = b'\x01'

class Message:
    def __init__(self, type: bytes, content: str):
        assert len(type) == len(OK)
        self.type = type
        self.content = content

def ok_message():
    return Message(OK, '')

def new_node_message():
    return Message(NEW_NODE, '')