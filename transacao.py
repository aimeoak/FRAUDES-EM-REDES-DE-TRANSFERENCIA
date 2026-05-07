class Transacao:
    def __init__(self, conta_origem, conta_destino, valor):
        self.conta_origem = conta_origem
        self.conta_destino = conta_destino
        self.valor = valor

    def __str__(self):
        return f"{self.conta_origem} ---> {self.conta_destino} | R${self.valor:.2f}"