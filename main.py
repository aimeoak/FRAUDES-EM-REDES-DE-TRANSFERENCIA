from leitor_csv import Leitor_csv
from visualizador import Visualizador
from ontologia import GerenciadorOntologia
from owlready2 import sync_reasoner # Importando o motor de inferência

if __name__ == "__main__":
    
    l = Leitor_csv()
    g = l.carregar("lista_transacoes.csv") 
    v = Visualizador()
    
    print(f" -> Total de contas monitoradas: {len(g.contas)}")
    print(f" -> Total de transações registradas: {len(g.transacoes)}")

   
    print("\n[1/3] EXECUTANDO ANÁLISE TOPOLÓGICA (GRAFO)...")
    tem_ciclo = g.detectar_ciclo()
    print(f" -> Alerta Estrutural: Detectado ciclo de lavagem de dinheiro? {'[SIM]' if tem_ciclo else '[NÃO]'}")
    
   
    print("\n[2/3] EXECUTANDO MODELAGEM ONTOLÓGICA...")
    onto_manager = GerenciadorOntologia()
    onto_manager.povoar_com_grafo(g)
    
    print("Classificando contas com base em regras")
    onto_manager.classificar_contas(g)

    print(" Motor de Inferência para validação lógica...")
    with onto_manager.onto:
        sync_reasoner()
        

    onto_manager.onto.save(file="resultado_fraudes.owl", format="rdfxml")
    print(" -> Ontologia exportada com sucesso para 'resultado_fraudes.owl'.")

    
    print("\n=============================================")
    print("                   Análise      ")
    print("=============================================")
    
    
    laranjas = onto_manager.onto.ContaLaranja.instances()
    concentradoras = onto_manager.onto.ContaConcentradora.instances()
    
    # Filtra suspeitas gerais para não repetir as que já são laranjas/concentradoras
    suspeitas = [c for c in onto_manager.onto.ContaSuspeita.instances() 
                 if c not in laranjas and c not in concentradoras]

    print(f"\n[!] Contas de Pulverização (Laranjas/Mulas) ({len(laranjas)} detectadas):")
    if not laranjas: print(" -> Nenhuma")
    for c in laranjas:
        print(f" -> {c.name}")
        
    print(f"\n[!] Contas de Acúmulo (Concentradoras/Cofre) ({len(concentradoras)} detectadas):")
    if not concentradoras: print(" -> Nenhuma")
    for c in concentradoras:
        print(f" -> {c.name}")
    
    print(f"\n[?] Alerta de Score: Outras Contas Suspeitas ({len(suspeitas)} detectadas):")
    if not suspeitas: print(" -> Nenhuma")
    for c in suspeitas:
        print(f" -> {c.name} (Score: {g.pontuacao_suspeita(c.name)})")

    print("\n=============================================")
    print("Gerando visualização gráfica da rede...")

    v.desenhar_grafo(g)