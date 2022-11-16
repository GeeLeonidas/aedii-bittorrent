## Decidir a implementação da descoberta: via tracker ou DHT circular?
## Via tracker parece ser mais simples, porém DHT circular é mais descentralizada
## Talvez algo entre ambos, um tracker distribuído implementado usando DHT circular

import socket as skt
import mensagem as msg

HOST = 'localhost'
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

## create a tcp socket that listens for incoming connections
def listen():
    s = skt.socket(skt.AF_INET)
    s.bind((HOST, PORT))
    s.listen()
    print ('Escutando')
    while True:
        conn, addr = s.accept()
        
        ## receive message
        data = conn.recv(1024)
        data_string = pickle.loads(data)
        print('Message received')
        print(data_string)

        ## handle message
        if data_string.tipo == 'REQUEST':
            ## TODO: Tratar a mensagem
            pass
        elif data_string.tipo == 'RESPONSE':
            ## TODO: Tratar a mensagem
            pass
        else:
            print('Unknown message type')
        

## send a message to a peer
def send_request(mensagem : msg.mensagem, ip : str, port : int):
    s = skt.socket(skt.AF_INET)
    s.connect((ip, port))
    data_string = pickle.dumps(mensagem)
    s.send(data_string)
    print('Message sent')
    s.close()


## create a message and send it to a peer
def send_test(ip : str, port : int):
    m = msg.mensagem('TEST', skt.gethostbyname(skt.gethostname()), PORT, 'BELA CHAVE')
    m.chave = input('Digite a chave: ') ## input message text (for testing)
    send_request(m, ip, port)


## Trata uma mensagem recebida do tipo REQUEST
##def handle_request(mensagem : msg.mensagem):

## Trata uma mensagem recebida do tipo RESPONSE
##def handle_response(mensagem : msg.mensagem):

