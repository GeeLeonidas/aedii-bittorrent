CHUNK_SIZE = 1 << 18 # 2^18 = 262144

## Pega um pedaço do arquivo, tamanho definido por `CHUNK_SIZE`
def get_chunk(filename: str, idx: int):
    with open(filename, mode='rb') as file:
        print("Getting chunk...")
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
        
            