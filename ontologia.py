from owlready2 import*


class GerenciadorOntologia:
    def __init__(self):
        self.onto = get_ontology("http://projetografo.com/financeiro.owl")
        self.definir_modelo()

    def definir_modelo(self):
        
        with self.onto:
            # Classes
            class Entidade(Thing): pass
            class PessoaFisica(Entidade): pass
            class PessoaJuridica(Entidade): pass

            class Conta(Thing): pass
            class ContaCorrente(Conta): pass
            class ContaSuspeita(Conta):pass
            class ContaLaranja(Conta): pass

            class Transacao(Thing): pass

            # Relações
            class pertence_a(ObjectProperty):
                domain = [Conta]
                range = [Entidade]
            class origina_transacao(ObjectProperty): 
                domain = [Conta]
                range = [Transacao]
                
            class recebe_transacao(ObjectProperty):
                domain = [Transacao]
                range = [Conta]

            
            class possui_valor(DataProperty):
                domain = [Transacao]
                range = [float]
        
    
    def povoar_com_grafo(self, grafo):
        #Transforama dados do grafo em individuos da ontologia
        with self.onto:
            dicionario_contas = {}
            #cria individuos classe conta
            for conta_id in grafo.contas:
                nova_conta = self.onto.ContaCorrente(conta_id)
                dicionario_contas[conta_id] = nova_conta
            for i,t in enumerate(grafo.transacoes):
                # Da o nome da transição
                nome_transacao = f"Transacao_{t.conta_origem}_para_{t.conta_destino}_{i}"
                nova_transacao = self.onto.Transacao(nome_transacao)

                # Adiciona o valor
                nova_transacao.possui_valor = [float(t.valor)]
                
                c_origem = dicionario_contas[t.conta_origem]
                c_destino = dicionario_contas[t.conta_destino]

                # Liga os nós
                c_origem.origina_transacao.append(nova_transacao)
                nova_transacao.recebe_transacao.append(c_destino)
    
    def classificar_contas(self, grafo):
        for conta_id in grafo.contas:
            
            enviado = grafo.total_valor_enviado(conta_id)
            recebido = grafo.total_valor_recebido(conta_id)
            entradas = grafo.grau_entrada(conta_id)
            saidas = grafo.grau_saida(conta_id)
            pontuacao_suspeita = grafo.pontuacao_suspeita(conta_id)
            
            conta_owl = self.onto.ContaCorrente(conta_id) 

            #CONTA LARANJA
            #Ela recebe de várias fontes, mas envia tudo para apenas um destino
            if entradas >= 2 and saidas == 1 and recebido > 0:
                taxa_repasse = enviado / recebido
                if taxa_repasse >= 0.80:  #Repassou 80% ou mais do que recebeu
                    conta_owl.is_a.append(self.onto.ContaLaranja)

            #CONTA SUSPEITA 
            #Parâmetros do score 
            if pontuacao_suspeita>=50: 
                conta_owl.is_a.append(self.onto.ContaSuspeita)
       

    def salvar_arquivo(self, nome_arquivo="minha_ontologia.owl"):
        self.onto.save(file=nome_arquivo, format="rdfxml")
        print(f"Ontologia salva com sucesso em {nome_arquivo}")



        
    