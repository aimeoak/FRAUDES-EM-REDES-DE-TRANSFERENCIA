from leitor_csv import Leitor_csv
from visualizador import Visualizador
from ontologia import GerenciadorOntologia




if __name__ == "__main__":
    
    l = Leitor_csv()
    g = l.carregar("lista_transacoes.csv") 
    v = Visualizador()
    print(f"Total de contas monitoradas: {len(g.contas)}")
    print(f"Total de transações registradas: {len(g.transacoes)}")

    # 2. Análise Estrutural (Grafo)
    print("ANÁLISE TOPOLÓGICA")
    tem_ciclo = g.detectar_ciclo()
    print(f"Alerta Estrutural: Detectado ciclo (dinheiro andando em círculos)? {'[SIM]' if tem_ciclo else '[NÃO]'}")
    
    
    print(f"Existe caminho conectando N1 (alto valor) a A1? {'SIM' if g.existe_caminho('N1', 'A1') else 'NÃO'}")

    
    print("ONTOLOGIA")
    onto_manager = GerenciadorOntologia()
    onto_manager.povoar_com_grafo(g)
    
    print("Classificando contas com base no comportamento financeiro")
    onto_manager.classificar_contas(g)

    #Resultado
    print("\n=============================================")
    print("      RELATÓRIO   ")
    print("=============================================")
    
    
    laranjas = onto_manager.onto.ContaLaranja.instances()
    fantasmas = onto_manager.onto.ContaFantasma.instances()

    print(f"\n[!] Contas tipo 'Laranja' ({len(laranjas)} detectadas):")
    if not laranjas: print(" -> Nenhuma")
    for c in laranjas:
        print(f" -> {c.name}")

    print(f"\n[!] Contas tipo 'Fantasma' ({len(fantasmas)} detectadas):")
    if not fantasmas: print(" -> Nenhuma")
    for c in fantasmas:
        print(f" -> {c.name}")

    print("\n=============================================")

    v.desenhar_grafo(g)