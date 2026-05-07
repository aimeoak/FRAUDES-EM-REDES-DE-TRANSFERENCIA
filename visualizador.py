import networkx as nx
import matplotlib.pyplot as plt

class Visualizador:
    def __init__(self):
        pass

    def desenhar_grafo(self,grafo):
        dg = nx.DiGraph()

        for t in grafo.transacoes:
            dg.add_edge(t.conta_origem, t.conta_destino, weight=t.valor)
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(dg, k=2, seed=42)
        nx.draw(dg, pos, with_labels=True, node_size=1200,font_size=10 ,node_color="lightblue")
        labels = nx.get_edge_attributes(dg, 'weight')
        nx.draw_networkx_edge_labels(dg, pos, edge_labels=labels, font_size=8)
        plt.show()