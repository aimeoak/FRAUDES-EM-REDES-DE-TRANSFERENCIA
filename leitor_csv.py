import csv
from grafo_transacoes import Grafo
class Leitor_csv:
    def __init__(self):
        pass

    def carregar(self, caminho):
        g = Grafo()
        with open(caminho, 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=",")

            for linha in csv_reader:
                vertice_origem = linha["conta_id1"]
                vertice_destino = linha["conta_id2"]
                valor = float(linha["valor"])

                g.adicionar_transacao(vertice_origem,vertice_destino,valor)
            return g
