from conta import Conta
from transacao import Transacao

class Grafo:
    def __init__(self):
        self.contas = {}
        self.transacoes = []
    
    def adicionar_conta(self,id):
        id = str(id)
        if id not in self.contas:
            self.contas[id] = Conta(id)

    def adicionar_transacao(self, conta_origem, conta_destino,valor):
        if conta_origem == conta_destino:
            return
        else:
            if conta_origem not in self.contas:
                self.adicionar_conta(conta_origem)
            if conta_destino not in self.contas:
                self.adicionar_conta(conta_destino)
            t = Transacao(conta_origem, conta_destino, valor)
            self.transacoes.append(t)
            return t
        
    def lista_transacoes_enviadas(self, conta_id):
        transacoes_enviadas = [t for t in self.transacoes if t.conta_origem == conta_id]
        return transacoes_enviadas
    
    def lista_transacoes_recebidas(self, conta_id):
        transacoes_recebidas = [t for t in self.transacoes if t.conta_destino == conta_id]
        return transacoes_recebidas
    
    def grau(self,conta_id):
        num_enviado = len(self.lista_transacoes_enviadas(conta_id))
        num_recebido = len(self.lista_transacoes_recebidas(conta_id))
        grau = num_enviado + num_recebido
        return grau
    
    def grau_saida(self, conta_id):
        num_enviado = len(self.lista_transacoes_enviadas(conta_id))
        return num_enviado
    
    def grau_entrada(self, conta_id):
        num_recebido = len(self.lista_transacoes_recebidas(conta_id))
        return num_recebido
    
    #Novas funçoes
    def total_valor_enviado(self, conta_id):
        transacoes = self.lista_transacoes_enviadas(conta_id)

        total = 0
        for t in transacoes:
            total+= t.valor 

        return total 

    def total_valor_recebido(self, conta_id): 
        transacoes = self.lista_transacoes_recebidas(conta_id)

        total = 0
        for t in transacoes:
            total+= t.valor 

        return total 
    
    def existe_caminho(self, conta1,conta2):
        
        visitados = set()

        def dfs(conta_atual):
            if conta_atual == conta2: 
                return True 

            visitados.add(conta_atual)

            transacoes = self.lista_transacoes_enviadas(conta_atual)

            for t in transacoes:
                vizinho = t.conta_destino 

                if vizinho not in visitados: 
                    if dfs(vizinho):
                        return True 

            return False 
        
        return dfs(conta1)
    
    def detectar_ciclo(self):

        visitados = set()
        pilha = set() 

        def dfs(conta): 
            visitados.add(conta)
            pilha.add(conta)

            transacoes = self.lista_transacoes_enviadas(conta)

            for t in transacoes:

                vizinho = t.conta_destino

                if vizinho not in visitados:
                    if dfs(vizinho): 
                        return True

                elif vizinho in pilha:
                        return True  
            
            pilha.remove(conta)
        
            return False 
    
        for conta in self.contas:
            if conta not in visitados: 
                if dfs(conta):
                    return True 
        return False