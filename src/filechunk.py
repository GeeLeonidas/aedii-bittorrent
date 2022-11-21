import socket as skt
import pickle as pk
from message import Message, ChunkMessage
import message
import random
import os

CHUNK_SIZE = 1 << 18  # = 2^18 = 262144


# Pega um pedaço do arquivo, tamanho definido por ''CHUNK_SIZE''
def get_chunk(filename: str, idx: int):
    with open(filename, mode='rb') as file:
        print("Getting chunk...")
        file.seek(CHUNK_SIZE * idx)
        return file.read(CHUNK_SIZE)


def convert_filename(filename: str):
    filename_conv = [0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,  # Aceita apenas os primeiros 64 caracteres
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(len(filename_conv)):
        if i >= len(filename):
            break
        filename_conv[i] = ord(filename[i])
        if i + 1 >= len(filename):
            break
        filename_conv[i] |= ord(filename[i + 1]) << 16
    return (filename_conv[0], filename_conv[1], filename_conv[2], filename_conv[3],
            filename_conv[4], filename_conv[5], filename_conv[6], filename_conv[7],
            filename_conv[8], filename_conv[9], filename_conv[10], filename_conv[11],
            filename_conv[12], filename_conv[13], filename_conv[14], filename_conv[15],
            filename_conv[16], filename_conv[17], filename_conv[18], filename_conv[19],
            filename_conv[20], filename_conv[21], filename_conv[22], filename_conv[23],
            filename_conv[24], filename_conv[25], filename_conv[26], filename_conv[27],
            filename_conv[28], filename_conv[29], filename_conv[30], filename_conv[31])


# Adiciona todos os pedaços de um arquivo à DHT
def add_file(path: str, filename: str, ip_list: list):
    # ip list é uma lista de tuplas (ip, porta)
    idx = 0
    chunk = get_chunk(f'{path}/{filename}', 0)
    while chunk != b'':
        msg: Message = message.put_file(None)
        find_msg: Message = message.find_file((filename, idx), None)
        chunk_msg = ChunkMessage((filename, idx), chunk)

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
        chunk = get_chunk(f'{path}/{filename}', idx)


# Reconstroi o arquivo a partir da lista de hashes
def reconstruct_file(path: str, filename: str, chunks: list):
    print("Reconstructing file...")
    os.makedirs(path, exist_ok=True)
    with open(f'{path}/{filename}', 'wb') as f:
        for chunk in chunks:
            f.write(chunk)


# Pede todos os pedaços de um arquivo à DHT, para quando receber ''FILE_NOT_FOUND''
def get_file(path: str, filename: str, ip_list: list):
    # send a message for each chunk to the server
    idx = 0
    returned_messages = []

    finder_addr = random.choice(ip_list)

    while True:
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(finder_addr)
            s.sendall(pk.dumps(message.find_file((filename, idx), None)))
            data = s.recv(1024)
            ff_msg: Message = pk.loads(data)

        if ff_msg.type == message.FILE_FOUND:
            with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as get_skt:
                target_ip, target_port = ff_msg.content.split(':')
                get_skt.connect((target_ip, int(target_port)))
                get_skt.sendall(pk.dumps(message.get_file((filename, idx), None)))

                response_msg_data = b''
                while True:  # Recebe ChunkMessage em pedaços
                    suffix_data = get_skt.recv(4096)
                    if suffix_data:
                        response_msg_data += suffix_data
                    if len(suffix_data) < 4096:
                        break
                response_msg: ChunkMessage = pk.loads(response_msg_data)
                returned_messages.append(response_msg.raw)
        else:
            assert ff_msg.type == message.FILE_NOT_FOUND
            break
        idx += 1

    if idx > 0:  # Encontrou pelo menos uma parte
        reconstruct_file(path, filename, returned_messages)
        print(f'Arquivo salvo como: {path}/{filename}')
    else:
        print(f'Arquivo com nome "{filename}" não foi encontrado!')
