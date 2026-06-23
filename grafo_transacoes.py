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

    def participa_ciclo(self, conta_inicial):

        visitados = set()
        pilha = set()

        def dfs(conta):

            visitados.add(conta)
            pilha.add(conta)

            transacoes = self.lista_transacoes_enviadas(conta)

            for t in transacoes:

                vizinho = t.conta_destino

                if vizinho == conta_inicial:
                    return True

                if vizinho not in visitados:
                    if dfs(vizinho):
                        return True

            pilha.remove(conta)

            return False

        return dfs(conta_inicial)
    def pontuacao_suspeita(self, conta_id):
        pontos = 0
        
        grau_total = self.grau(conta_id)
        saidas = self.grau_saida(conta_id)
        enviado = self.total_valor_enviado(conta_id)
        recebido = self.total_valor_recebido(conta_id)

        todos_enviados = [self.total_valor_enviado(c) for c in self.contas if self.total_valor_enviado(c) > 0]
        todos_enviados.sort()

        if len(todos_enviados) > 0:
            indice_p75 = int(len(todos_enviados) * 0.75)
            indice_p90 = int(len(todos_enviados) * 0.90)
            
            limite_volume_alto = todos_enviados[indice_p75]    # Os 25% que mais enviam
            limite_volume_extremo = todos_enviados[indice_p90] # Os 10% que mais enviam
        else:
            limite_volume_alto = float('inf')
            limite_volume_extremo = float('inf')

        
        #Lavagem
        if self.participa_ciclo(conta_id):
            pontos += 40 

        #Muitas interações
        if grau_total > 5:
            pontos += 10
        if grau_total > 10:
            pontos += 15 
            
        if saidas > 5:
            pontos += 10

        
        if recebido > 0:
            # Repasse Alto
            if enviado >= (recebido * 0.90):
                pontos += 20
                
            # Conta Ponte
            diferenca = abs(enviado - recebido)
            limite_taxa = recebido * 0.05 
            if diferenca <= limite_taxa:
                pontos += 15

        if enviado >= limite_volume_alto:
            pontos += 10
            
        if enviado >= limite_volume_extremo:
            pontos += 15 

        return min(pontos, 100)