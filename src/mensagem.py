class mensagem:
    tipo = ''
    ipOrigem = ''
    portOrigem = ''
    chave = ''

    def __init__(self, tipo, ipOrigem, portOrigem, chave):
        self.tipo = tipo
        self.ipOrigem = ipOrigem
        self.portOrigem = portOrigem
        self.chave = chave
    
    def __str__(self):
        return self.tipo + " " + self.ipOrigem + " " + str(self.portOrigem) + " " + self.chave

    
