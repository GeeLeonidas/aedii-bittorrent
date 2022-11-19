import socket as skt
import pickle as pk
from message import Message
import message
import sys
import filechunk

class client:

    def __init__(self, server: str, port: str):
        self.server = server
        self.port = port
    
    def get_file(self, file_name: str):
        
        # send a message for each chunk to the server
        idx = 0
        returned_messages = []
        
        while True:
            with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                s.connect((self.server, self.port))
                s.sendall(pk.dumps(message.get_file_message(file_name, idx)))
                data = s.recv(1024)
                msg: Message = pk.loads(data)
                returned_messages.append(msg)
                idx += 1
                s.close()
                if msg.content[2] == True:
                    break

        # reconstruct the file
        filechunk.reconstruct_file(file_name, [msg.content[0] for msg in returned_messages])
        
        print("File received: ", file_name)
