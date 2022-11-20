import socket as skt
import pickle as pk
from message import Message, ChunkMessage
import message
import random

CHUNK_SIZE = 1 << 18 # = 2^18 = 262144

## Pega um pedaço do arquivo, tamanho definido por `CHUNK_SIZE`
def get_chunk(filename: str, idx: int):
    with open(filename, mode='rb') as file:
        print("Getting chunk...")
        file.seek(CHUNK_SIZE * idx)
        return file.read(CHUNK_SIZE)

def convert_filename(filename: str):
    filename_conv = [0, 0, 0, 0, 0, 0, 0, 0, # Aceita apenas os primeiros 32 caracteres
                     0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(filename_conv)):
        if i >= len(filename):
            break
        filename_conv[i] = ord(filename[i])
        if i+1 >= len(filename):
            break
        filename_conv[i] |= ord(filename[i+1]) << 16
    return (filename_conv[0], filename_conv[1], filename_conv[2], filename_conv[3],
            filename_conv[4], filename_conv[5], filename_conv[6], filename_conv[7],
            filename_conv[8], filename_conv[9], filename_conv[10], filename_conv[11],
            filename_conv[12], filename_conv[13], filename_conv[14], filename_conv[15])

## Adiciona todos os pedaços de um arquivo à DHT
def add_file(filename: str , ip_list : list):
    # ip list é uma lista de tuplas (ip, porta)
    idx = 0
    chunk = get_chunk(filename, 0)
    while chunk != b'':
        msg: Message = message.put_file(None)
        find_msg: Message = message.find_file((filename, idx), None)
        chunk_msg = ChunkMessage((filename, idx), chunk)
        file_addr = None
        
        # Select a random ip from the list
        ip = random.choice(ip_list)
        
        # Envia a mensagem para o ip selecionado
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(ip)
            s.sendall(pk.dumps(find_msg))
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg == message.FILE_FOUND or response_msg.type == message.FILE_NOT_FOUND
            file_ip, file_port = response_msg.content.split(':')
            file_addr = (file_ip, int(file_port))
        
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(file_addr)
            s.sendall(pk.dumps(msg))
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK
            s.sendall(pk.dumps(chunk_msg))

        idx += 1
        chunk = get_chunk(filename, idx)
        
            



## Retorna uma lista com os hashes dos pedaços do arquivo
def get_file(filename: str) -> list:
    res = []
    idx = 0
    chunk = get_chunk(filename, 0)
    print("Getting file...")
    while chunk != b'':
        res.append(chunk)
        idx += 1
        chunk = get_chunk(filename, idx)
        print("Chunk: ", chunk)
    return res

## Reconstroi o arquivo a partir da lista de hashes
def reconstruct_file(filename: str, chunks: list):
    print("Reconstructing file...")
    with open(filename, 'ab') as f:
        for chunk in chunks:
            f.write(chunk)
        
            