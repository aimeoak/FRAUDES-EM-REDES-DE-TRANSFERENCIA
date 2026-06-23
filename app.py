import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components


@st.cache_data
def carregar_dados():
    df = pd.read_csv("lista_transacoes.csv")
    return df

def construir_grafo_estrutural(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['conta_id1'], row['conta_id2'], weight=row['valor'])
    return G


# Ontologia
def aplicar_ontologia(G):
    """
    Aplica as regras de negócio e calcula o Score de Risco dinamicamente.
    """
    
    # Limite Recebido (Para Conta Concentradora)
    valores_recebidos = [sum([d['weight'] for u, v, d in G.in_edges(n, data=True)]) for n in G.nodes()]
    valores_recebidos.sort()
    limite_p90_recebido = valores_recebidos[int(len(valores_recebidos) * 0.90)] if valores_recebidos else 1.0
    if limite_p90_recebido == 0: limite_p90_recebido = 1.0

    # Limites Enviados (Para Score de Risco)
    valores_enviados = [sum([d['weight'] for u, v, d in G.out_edges(n, data=True)]) for n in G.nodes()]
    enviados_validos = [v for v in valores_enviados if v > 0] # Ignora quem enviou zero
    enviados_validos.sort()
    
    if len(enviados_validos) > 0:
        limite_vol_alto = enviados_validos[int(len(enviados_validos) * 0.75)]
        limite_vol_extremo = enviados_validos[int(len(enviados_validos) * 0.90)]
    else:
        limite_vol_alto = float('inf')
        limite_vol_extremo = float('inf')

    # Detecta quem participa de ciclos (Lavagem)
    ciclos = list(nx.simple_cycles(G))
    nos_em_ciclos = set()
    for c in ciclos:
        nos_em_ciclos.update(c)

    #Pontuação e classificacao
    for node in G.nodes():
        entradas = G.in_degree(node)
        saidas = G.out_degree(node)
        grau_total = G.degree(node)
        recebido = sum([d['weight'] for u, v, d in G.in_edges(node, data=True)])
        enviado = sum([d['weight'] for u, v, d in G.out_edges(node, data=True)])

        #calculo score
        pontos = 0
        if node in nos_em_ciclos: pontos += 40
        if grau_total > 5: pontos += 10
        if grau_total > 10: pontos += 15
        if saidas > 5: pontos += 10

        if recebido > 0:
            if enviado >= (recebido * 0.90): pontos += 20
            diferenca = abs(enviado - recebido)
            if diferenca <= (recebido * 0.05): pontos += 15

        if enviado >= limite_vol_alto: pontos += 10
        if enviado >= limite_vol_extremo: pontos += 15

        pontos = min(pontos, 100) # Trava o score em 100
        
        G.nodes[node]['score'] = pontos

        # classificacao final
        G.nodes[node]['tipo_semantico'] = 'Conta Normal'
        G.nodes[node]['cor'] = '#97c2fc' # Azul padrão
        
        # Laranja
        if entradas >= 2 and saidas > 0 and saidas <= 2:
            if recebido > 0 and (enviado / recebido) >= 0.85:
                G.nodes[node]['tipo_semantico'] = 'Conta Laranja'
                G.nodes[node]['cor'] = '#ffcc00' # Amarelo alerta
                
        #Concentradora
        elif entradas >= 3 and saidas == 0 and recebido >= limite_p90_recebido:
            G.nodes[node]['tipo_semantico'] = 'Conta Concentradora'
            G.nodes[node]['cor'] = '#ff3333' # Vermelho perigo

        #Conta Suspeita 
        elif pontos >= 50:
            G.nodes[node]['tipo_semantico'] = 'Conta Suspeita'
            G.nodes[node]['cor'] = '#ff8c00' # Laranja escuro / Alerta

    return G


def desenhar_grafo_pyvis(G, nome_arquivo, usar_semantica=False):
    net = Network(height='700px', width='100%', directed=True, bgcolor='#222222', font_color='white')
    
    for node, data in G.nodes(data=True):
        cor = data.get('cor', '#97c2fc') if usar_semantica else '#97c2fc'
        titulo = f"Conta: {node}\nTipo: {data.get('tipo_semantico', 'Desconhecido')}" if usar_semantica else f"Conta: {node}"
        
        net.add_node(node, label=str(node), title=titulo, color=cor, size=25)
        
    for source, target, data in G.edges(data=True):
        peso = data['weight']
        net.add_edge(source, target, title=f"Valor: R$ {peso}", value=peso)
        
    net.show_buttons(filter_=['physics']) 
    
    net.save_graph(nome_arquivo)
    return nome_arquivo


# INTERFACE
st.set_page_config(page_title="Monitor de Fraudes (PLD)", layout="wide")
st.title("Detecção de Fraudes Financeiras com Grafos e Semântica")

df = carregar_dados()
G_estrutural = construir_grafo_estrutural(df)
G_semantico = aplicar_ontologia(G_estrutural.copy())

tab1, tab2, tab3, tab4 = st.tabs(["1. Dados Brutos", "2. Análise Topológica", "3. Grafo Semântico", "4. Comparação (O Valor da Ontologia)"])

#CAMILA: Adc mais métricas estruturais
with tab1:
    st.header("Dados de Origem (Arestas)")
    st.dataframe(df, use_container_width=True)
    st.write(f"**Total de Contas (Vértices):** {G_estrutural.number_of_nodes()}")
    st.write(f"**Total de Transações (Arestas):** {G_estrutural.number_of_edges()}")

with tab2:
    st.header("Análise Estrutural (Apenas Conexões)")
    st.write("Aqui o algoritmo enxerga apenas a topologia da rede. Como ainda não aplicamos as regras da Ontologia, todos os nós são vistos da mesma forma, sem distinção de risco.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Métrica: Contas com Mais Conexões")
        graus = sorted(G_estrutural.degree, key=lambda x: x[1], reverse=True)[:5]
        for conta, grau in graus:
            st.write(f"- **{conta}**: {grau} conexões")
            
    with col2:
        st.subheader("Alerta Topológico: Ciclos")
        # Encontra os ciclos dinamicamente usando o NetworkX
        ciclos = list(nx.simple_cycles(G_estrutural))
        
        
        ciclos_reais = [c for c in ciclos if len(c) > 2] 
        
        if ciclos_reais:
            st.error(f"Detectamos {len(ciclos_reais)} ciclo(s) na rede.")
            
            for i, ciclo in enumerate(ciclos_reais):
                caminho = " -> ".join(map(str, ciclo))
                st.write(f"**Ciclo {i+1}:** {caminho} -> {ciclo[0]}")
        else:
            st.success("Nenhum ciclo fechado detectado.")

    st.subheader("Visualização Topológica (Sem Semântica)")
    
    
    arq_html_estrutural = desenhar_grafo_pyvis(G_estrutural, "grafo_estrutural.html", usar_semantica=False)
    

    with open(arq_html_estrutural, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=700)

with tab3:
    st.header("Análise Semântica)")
    st.write("Aplicamos as regras da Ontologia (Limites Dinâmicos e Taxa de Repasse). Veja quem o sistema classificou como criminoso:")
    
    # Filtra as contas classificadas
    laranjas = [n for n, d in G_semantico.nodes(data=True) if d['tipo_semantico'] == 'Conta Laranja']
    concentradoras = [n for n, d in G_semantico.nodes(data=True) if d['tipo_semantico'] == 'Conta Concentradora']
    suspeitas = [f"{n} (Score: {d['score']})" for n, d in G_semantico.nodes(data=True) if d['tipo_semantico'] == 'Conta Suspeita']
    
    st.markdown("""
    **Legenda do Grafo Semântico:**
    * 🔵 **Azul:** Conta Normal 
    * 🟠 **Laranja Escuro:** Conta Suspeita (Score de Risco ≥ 50)
    * 🟡 **Amarelo:** Conta Laranja (Funil de Pulverização)
    * 🔴 **Vermelho:** Conta Concentradora (Cofre final)
    """)
    
    colA, colB, colC = st.columns(3)
    with colA:
        st.warning(f"🟡 **Laranjas:** {', '.join(laranjas) if laranjas else 'Nenhuma'}")
    with colB:
        st.error(f"🔴 **Concentradoras:** {', '.join(concentradoras) if concentradoras else 'Nenhuma'}")
    with colC:
        st.info(f"🟠 **Suspeitas:** {', '.join(suspeitas) if suspeitas else 'Nenhuma'}")
    
    st.subheader("Grafo Semântico Interativo")
   
    arq_html_semantico = desenhar_grafo_pyvis(G_semantico, "grafo_semantico.html", usar_semantica=True)
    
    with open(arq_html_semantico, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=700)

#CAMILA: ADC alguma relação com caminho mínimo/ complementar essa página
with tab4:
    st.header("Por que a Semântica importa?")
    st.markdown("""
    **Sem a Ontologia (Aba 2):** O sistema sabe que a conta *EMP1* tem muitas conexões e a conta *Z1* também. Para um grafo puramente matemático, ambas são apenas "nós de alto grau". Isso gera falsos positivos, bloqueando a conta da empresa que só está pagando salários.
    
    **Com a Ontologia (Aba 3):** Ao introduzir regras semânticas de domínio, o sistema entende o **significado** da topologia. Ele percebe que *EMP1* é uma origem legítima (só sai dinheiro), enquanto *Z1* é um "cofre" que concentra dinheiro possivelmente sujo. 
    
    *Resultado: A semântica transforma dados brutos em inteligência.*
    """)