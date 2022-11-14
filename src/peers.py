## Decidir a implementação da descoberta: via tracker ou DHT circular?
## Via tracker parece ser mais simples, porém DHT circular é mais descentralizada
## Talvez algo entre ambos, um tracker distribuído implementado usando DHT circular

import socket as skt

PORT = 33333
CHUNK_SIZE = 1 << 18 # 2^18 = 262144

## Conecta à DHT
## Retorna: O id do cliente
def connect(target_ip: str) -> int:
    s = skt.socket(skt.AF_INET)
    s.connect((target_ip, PORT))
    # TODO: Propagar a divulgação do novo nó

## Pega um pedaço do arquivo, tamanho definido por `CHUNK_SIZE`
def get_chunk(filename: str, idx: int) -> str:
    with open(filename, mode='r') as file:
        file.seek(CHUNK_SIZE * idx)
        return file.read(CHUNK_SIZE)

## Adiciona todos os pedaços de um arquivo à DHT
## Retorna: Uma lista com os hashes dos pedaços
def add_file(filename: str) -> list:
    res = []
    idx = 0
    chunk = get_chunk(filename, 0)
    while chunk != '':
        chunk_hash = hash(chunk)
        # TODO: Inserir o hash do pedaço à DHT (tratando colisões)
        res.append(chunk_hash)
        idx += 1
        chunk = get_chunk(filename, idx)
    return res