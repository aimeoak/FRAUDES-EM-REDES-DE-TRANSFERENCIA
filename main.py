from leitor_csv import Leitor_csv
from visualizador import Visualizador
class gerenciador:



    if __name__ == "__main__":
        #Aqui eu tava só testando se tava as funções ok, mas coloca aqui alguns testes de nós suspeitos 
        l = Leitor_csv()
        v = Visualizador()
        g = l.carregar("lista_transacoes.csv")
        v.desenhar_grafo(g)
        x = g.lista_transacoes_recebidas("G1")
        for t in x:
            print(t)
        y = g.lista_transacoes_enviadas("G1")
        for t in y:
            print(t)
        print(g.grau("G1"))
        print(g.grau_entrada("G1"))
        print(g.grau_saida("G1"))
        #testes das novas funções
        print(g.total_valor_enviado("G1"))
        print(g.total_valor_recebido("G1"))
        print(g.existe_caminho("G1","B3"))
        print(g.detectar_ciclo())