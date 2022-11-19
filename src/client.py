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
        # get chunk list of file
        chunk_list = filechunk.get_chunk_list(file_name)
        # send a message for each chunk to the server
        idx = 0
        returned_messages = []
        for chunk in chunk_list:
            with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
                s.connect((self.server, self.port))
                s.sendall(pk.dumps(message.get_file_message(chunk, idx)))
                data = s.recv(1024)
                msg: Message = pk.loads(data)
                returned_messages.append(msg)
                idx += 1
                s.close()
        
        # sort the messages by index
        returned_messages.sort(key=lambda x: x.index)

        # write the file
        with open(file_name, 'wb') as f:
            for msg in returned_messages:
                chunk = (msg.content.split(':'))[2]
                f.write(chunk)
                f.close()
        



        


