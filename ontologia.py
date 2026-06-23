from owlready2 import*


class GerenciadorOntologia:
    def __init__(self):
        self.onto = get_ontology("http://projetografo.com/financeiro.owl")
        self.definir_modelo()

    def definir_modelo(self):
        with self.onto:
            
        
            class Entidade(Thing): pass
            class PessoaFisica(Entidade): pass
            class PessoaJuridica(Entidade): pass
            AllDisjoint([PessoaFisica, PessoaJuridica]) 


            class Conta(Thing): pass
            class ContaCorrente(Conta): pass
            class ContaSuspeita(Conta): pass
            class ContaLaranja(ContaSuspeita): pass       
            class ContaConcentradora(ContaSuspeita): pass 

            AllDisjoint([Conta, Entidade]) 

            class Transacao(Thing): pass

      
            class pertence_a(ObjectProperty):
                domain = [Conta]
                range = [Entidade]
            
            class dono_da_conta(ObjectProperty):
                domain = [Entidade]
                range = [Conta]
                inverse_property = pertence_a 

            class origina_transacao(ObjectProperty): 
                domain = [Conta]
                range = [Transacao]
                
            class transacao_originada_por(ObjectProperty):
                domain = [Transacao]
                range = [Conta]
                inverse_property = origina_transacao 
                
            class recebe_transacao(ObjectProperty):
                domain = [Transacao]
                range = [Conta]

            class possui_valor(DataProperty):
                domain = [Transacao]
                range = [float]

    def povoar_com_grafo(self, grafo):
        
        with self.onto:
            dicionario_contas = {}
            
            for conta_id in grafo.contas:
                nova_conta = self.onto.ContaCorrente(conta_id)
                dicionario_contas[conta_id] = nova_conta
            for i,t in enumerate(grafo.transacoes):
                
                nome_transacao = f"Transacao_{t.conta_origem}_para_{t.conta_destino}_{i}"
                nova_transacao = self.onto.Transacao(nome_transacao)

                
                nova_transacao.possui_valor = [float(t.valor)]
                
                c_origem = dicionario_contas[t.conta_origem]
                c_destino = dicionario_contas[t.conta_destino]

                
                c_origem.origina_transacao.append(nova_transacao)
                nova_transacao.recebe_transacao.append(c_destino)
    
    def classificar_contas(self, grafo):
        
        valores_recebidos = []
        for conta_id in grafo.contas:
            valores_recebidos.append(grafo.total_valor_recebido(conta_id))
        
        valores_recebidos.sort()
        
        indice_p90 = int(len(valores_recebidos) * 0.90)
        
        limite_dinamico_concentradora = valores_recebidos[indice_p90]
        
        if limite_dinamico_concentradora == 0:
            limite_dinamico_concentradora = 1.0


        for conta_id in grafo.contas:
            enviado = grafo.total_valor_enviado(conta_id)
            recebido = grafo.total_valor_recebido(conta_id)
            entradas = grafo.grau_entrada(conta_id)
            saidas = grafo.grau_saida(conta_id)
            
            conta_owl = self.onto.ContaCorrente(conta_id) 

            # CONTA LARANJA
            if entradas >= 2 and saidas > 0 and saidas <= 2:
                if recebido > 0:
                    taxa_repasse = enviado / recebido
                    if taxa_repasse >= 0.85:  
                        conta_owl.is_a.append(self.onto.ContaLaranja)

            #CONTA CONCENTRADORA
            # Só é concentradora se recebeu valor igual ou maior que os Top 10% da rede
            if entradas >= 3 and saidas == 0 and recebido >= limite_dinamico_concentradora:
                conta_owl.is_a.append(self.onto.ContaConcentradora)
                
            #CONTA SUSPEITA GERAL (Score de Risco)
            pontuacao_suspeita = grafo.pontuacao_suspeita(conta_id)
            if pontuacao_suspeita >= 50: 
                conta_owl.is_a.append(self.onto.ContaSuspeita)

    def salvar_arquivo(self, nome_arquivo="minha_ontologia.owl"):
        self.onto.save(file=nome_arquivo, format="rdfxml")
        print(f"Ontologia salva com sucesso em {nome_arquivo}")



        
    