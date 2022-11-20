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
                s.sendall(pk.dumps(message.find_file((file_name, idx), s.getsockname())))
                data = s.recv(1024)

                ff_msg = pk.loads(data)

                if ff_msg.type == message.FILE_FOUND:
                    with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as get_skt:
                        get_skt.connect((ff_msg.content.split(':')[0], int(ff_msg.content.split(':')[1])))
                        get_skt.sendall(pk.dumps(message.get_file(get_skt.getsockname(), (file_name, idx))))
                        
                        response_msg_data = b''
                        while True: # Recebe ChunkMessage em pedaços
                            suffix_data = get_skt.recv(4096)
                            if not suffix_data:
                                break
                            response_msg_data += suffix_data
                        response_msg: Message = pk.loads(response_msg_data)
                        returned_messages.append(response_msg.content)
                else:
                    break
                idx += 1
        
        filechunk.reconstruct_file(file_name, returned_messages)
        
        print("File received: ", file_name)
