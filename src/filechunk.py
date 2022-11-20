import socket as skt
import pickle as pk
import message
import random

CHUNK_SIZE = 1 << 18 # 2^18 = 262144

## Pega um pedaço do arquivo, tamanho definido por `CHUNK_SIZE`
def get_chunk(filename: str, idx: int):
    with open(filename, mode='rb') as file:
        print("Getting chunk...")
        file.seek(CHUNK_SIZE * idx)
        return file.read(CHUNK_SIZE)

## Adiciona todos os pedaços de um arquivo à DHT
## Retorna: Uma lista com os hashes dos pedaços
def add_file(filename: str , ip_list : list):
    # ip list é uma lista de tuplas (ip, porta)
    idx = 0
    chunk = get_chunk(filename, 0)
    while chunk != b'':

        final = chunk == b''
        msg : message = message.put_file_message(filename, idx, chunk, final)
        
        # Select a random ip from the list
        ip = random.choice(ip_list)
        
        # Envia a mensagem para o ip selecionado
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect((ip[0], ip[1]))
            s.sendall(pk.dumps(msg))
            response_msg_data = s.recv(1024)
            response_msg: Message = pk.loads(response_msg_data)
            assert response_msg.type == message.OK

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
        
            