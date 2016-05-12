import copy

class Automato(object):
    """
    Automato com as operacoes de minimizacao, determinizacao e eliminacao de 
    epsilon transicoes, alem de outras operacoes basicas
    """
    #dado um estado, ele da um dicionario com todas as transicoes possiveis
    tabelaTransicao = {}
    alfabeto = set([])
    estados = set([])
    estadoInicial = ""
    estadosFinais = set([])
    
    def __init__(self, tabelaTransicao, alfabeto, estados, estadoInicial, estadosFinais):
        """
        Configura o automato atraves do parametros passados
        @tabelaTransicao: {{}} tabela de transicao onde a chave do primeiro dicionario
        eh um estado que mapeia para um dicionario onde a chave eh o simbolo de transicao
        e o valor eh o estado de destino. Caso queira representar nao determinismo, deve ser feito
        na forma de "S":{"a":"A,B"} que significa: S vai para A ou B atraves de a
        @alfabeto set() conjunto de simbolos de transicao do automato (strings)
        @estados set() conjunto de todos os estados do automato (strings)
        @estadoInicial string estado inicial do automato
        @estadosFinais set() conjunto de string que representam o estado final
        """
        self.tabelaTransicao = tabelaTransicao
        self.alfabeto = alfabeto
        self.estadoInicial = estadoInicial
        self.estados = estados
        self.estadosFinais = estadosFinais
        
    def determinizar(self):
        """
        Determiniza o automato passado, eliminando transicoes
        do tipo A: {a: B,C}
        """
        #lista de novos estados que irao compor o automato
        novosEstados = {}
        
        #determinado as transicoes do estado inicial
        transIniciais = self.tabelaTransicao.get( self.estadoInicial )
        
        aux = {}
        for i in transIniciais.keys():
            aux[i] = self.formatarNome( transIniciais.get(i) )  
        
        novosEstados[self.estadoInicial] = aux
        
        #isso eh necessario pq a lista de novos estados, mesmo qnd atualizada, se mantem imutavel ali no for
        for i in range(2**len(self.alfabeto)):
        
            #para cada um dos proximos estados
            for i in novosEstados.keys():
                
                #pega as transicoes partindo de i
                aux = novosEstados.get(i)
                
                for j in aux.values():
                    
                    #se esse estado ainda nao foi mapeado, mapeia
                    if not novosEstados.has_key(j) and j != "":
                        novoEstado = ""
                        temp = {}
                        for m in self.alfabeto:
                            novoEstado = ""
                            for k in j[:]:
    
                                if self.tabelaTransicao[k].has_key(m):
                                    novoEstado += self.formatarNome(self.tabelaTransicao[k][m])

                            #obs, adicionei esse if a seguir, verificar outros casos
                            if novoEstado: 
                                temp[m] = self.formatarNome(novoEstado)
                        
                        novosEstados[j] = temp.copy()

        self.atualizarEstados(novosEstados)
        self.atualizarEstadosFinais()
        self.atualizarEstadoInicial()
        self.renomearAutomato()
        
    def atualizarEstados(self, novosEstados):
        """
        Seta um novo valor para a tabela de transicao
        """
        self.tabelaTransicao = novosEstados
    
    def atualizarEstadosFinais(self):
        """
        Verifica quais dos novos estados sao finais
        em relacao aos antigos
        """
        novosFinais = set()
        for estado in self.tabelaTransicao.keys():
            for simbolo in estado:
                if estado != "ERRO" and simbolo in self.estadosFinais:
                    novosFinais.add(estado)
        self.estadosFinais = novosFinais
        
    def atualizarEstadoInicial(self):
        """
        Verifica qual estado eh inicial em relacao aos antigos
        """
        if not self.estadoInicial in self.tabelaTransicao.keys():
            for estado in self.tabelaTransicao.keys():
                for simbolo in estado:
                    if simbolo == self.estadoInicial:
                        self.estadoInicial = estado
       
    def ehDeterministico(self):
        """
        Verifica se o automato atual eh deterministico ou nao
        Retorna True ou False
        """
        for transicao in self.tabelaTransicao.values():
            for trans in transicao.values():
                if trans.count(",")>0:
                    return False
        return True
                        
    def minimizarAFD(self):
        """
        Minimiza o automato caso ele seja deterministo, caso contrario
        lanca uma excecao
        """
        if not self.ehDeterministico():
            raise ExcecaoMinimizarAutomatoNaoDeterministico("Determinize o automato antes.")
            return
        
        self.eliminarEstadosInalcancaveis()
        self.eliminarEstadosMortos()
        self.criarEstadosErro()
        
        #cria os dois conjuntos iniciais, o primeiro com os estados finais, e o segundo com os outros estados
        conjuntos = [set([est for est in self.estadosFinais if est in self.estados]),
                      set([est for est in self.tabelaTransicao if est not in self.estadosFinais]) ]

        classesEquivalencia = self.acharEstadosEquivalentes(conjuntos)

        self.criarNovosEstados(classesEquivalencia)
        self.atualizarEstadoInicial()
        self.atualizarEstadosFinais()
        self.renomearAutomato()

    def criarEstadosErro(self):
        """
        Criar estados de erro para tornar o automato completo
        """
        criarEstadoErro = False
        #procura os estados que nao sao completos para adicionar o estado de erro
        for chave in self.tabelaTransicao.keys():
           
            estadoTransicao = self.tabelaTransicao[chave]
            for letra in self.alfabeto:
                if not estadoTransicao.has_key(letra):
                    estadoTransicao[letra] = "ERRO"
                    criarEstadoErro = True
               
                    
            self.tabelaTransicao[chave] = estadoTransicao
            
        if criarEstadoErro:
            estadoErro = {}
            #cria o estado de erro e adiciona na tabela de transicoes
            for letra in self.alfabeto:
                estadoErro[letra] = "ERRO"
            self.tabelaTransicao["ERRO"] = estadoErro
        
    def criarNovosEstados(self,classesEquivalencia):
        """
        Cria os novos estados tendo por base a classe de equivalencia
        para minimizacao de automatos
        @classesEquivalencia eh um conjunto de conjuntos de estados equivalentes
        """

        novaTabela = {}
        for classe in classesEquivalencia:
            nome = ''.join([i for i in classe])
            nvT = {}
            a = classe.pop()
            classe.add(a)
            trans = self.tabelaTransicao.get(a)

            for i in trans:
                if trans.get(i) in classe:
                    estado = nome
                else:
                    for c in classesEquivalencia:
                        if trans.get(i) in c:
                            estado = ''.join([m for m in c])
                nvT[i] = self.formatarNome(estado)
                            
            novaTabela[self.formatarNome(nome)] = nvT
        self.tabelaTransicao = novaTabela
        
    def eliminarEstadosMortos(self):
        """
        Procura quais estados sao vivos e elimina todos os outros
        atualiza os dados do automato em seguida
        """
        estados = self.acharEstadosVivos(self.estadosFinais,[i for i in self.estadosFinais])
        self.tabelaTransicao = self.eliminarEstados(estados)
        self.estados = (self.tabelaTransicao.keys())
        self.estadosFinais = ([i for i in self.estadosFinais if i in estados])

    def eliminarEstadosInalcancaveis(self):
        """
        Procura quais estados sao alcancaveis e elimina todos os outros
        atualiza os dados do automato em seguida
        """
        estados = self.acharEstadosAlcancaveis(self.estadoInicial,[self.estadoInicial])
        self.tabelaTransicao = self.eliminarEstados(estados)
        self.estados = (self.tabelaTransicao.keys())
        self.estadosFinais = ([i for i in self.estadosFinais if i in estados])
    
    def acharEstadosEquivalentes(self, conjuntos):
        """
        Acha quais estados sao equivalentes entre si e retorna um conjunto
        com todos os estados equivalentes
        @conjuntos inicialmente um conjunto com todos os finais e outro com todos os que nao sao finais
        """
        classes_equivalencia = []
        acabou = True
        
        if(conjuntos[0] != set()):
            classes_equivalencia.append(conjuntos[0])
            if(conjuntos[1] != set()):
                classes_equivalencia.append(conjuntos[1])
             
        while(acabou):
            acabou = False
            classes_equivalencia_nova = []

            for classe in classes_equivalencia:
                estado_ref = classe.pop()
    
                classe1 = set()
                classe2 = set()
                classe1.add(copy.copy(estado_ref))
                classe.add(estado_ref) 
                for estado in classe:
                    if(self.estadosSaoEquivalentes(estado_ref, estado, classes_equivalencia)):
                        classe1.add(estado)
                    else:
                        classe2.add(estado)
               
                classes_equivalencia_nova.append(classe1)
                if(classe2 != set()):
                    acabou = True
                    classes_equivalencia_nova.append(classe2)
            classes_equivalencia = classes_equivalencia_nova

        return classes_equivalencia  
                 
    def estadosSaoEquivalentes(self,estado_referencia, estado, classes_equivalencia):
        """
        Recebe dois estados e verifica se sao equivalentes atraves dos conjuntos
        de classes de equivalencia
        @estado_referencia estado de referencia que eh usado para comparar o outro estado
        @estado estado que se quer saber se eh ou nao equivalente ao estado de referencia
        @classes_de_equivalencia conjunto de conjuntos de estados equivalentes
        """
        equivalentes = 0
        for letra in self.alfabeto:
            trans_ref = self.tabelaTransicao.get(estado_referencia).get(letra)
            trans = self.tabelaTransicao.get(estado).get(letra)
            
            for classe in classes_equivalencia:
                if((trans_ref in classe) and (trans in classe)):
                    equivalentes += 1
             
        return equivalentes == len(self.alfabeto)
        
    def acharEstadosVivos(self,estadosFinais,estados = []):
        """
        Acha todos os estados vivos do automato
        @estadosFinais estados finais do automato, pois primeiramente sao os unicos
        que a gente sabe que sao vivos
        """
        for est in estadosFinais:
            trans = self.tabelaTransicao.keys()
            for chave in trans:
                transicoes = self.tabelaTransicao.get(chave)
                for t in transicoes.values():
              
                    if (t == est and chave not in estados):
                        estados.append(chave)
                        self.acharEstadosVivos(chave, estados)
      
        return estados
    
    def eliminarEstados(self,estados):
        """
        Elimina todos os estados passado como parametro
        @estados conjunto de estados que se quer eliminar
        """
        novaTabela = {}
        for i in self.tabelaTransicao.keys():
            if i in estados:
                transicao = {}
                for trans in self.tabelaTransicao.get(i).keys():
                    if self.tabelaTransicao.get(i).get(trans) in estados:
                        transicao[trans] = self.tabelaTransicao.get(i).get(trans)
                novaTabela[i] = transicao
                
        
        return novaTabela
    
    def acharEstadosAlcancaveis(self, estado, estados = []):
        """
        Acha todos os estados alcancaveis do automato
        """
        possibilidades = self.tabelaTransicao.get(estado)
       
        for i in possibilidades.values():
            if i not in estados:
                estados.append(i)
                self.acharEstadosAlcancaveis(i, estados)
        
        return estados
        
    def formatarNome(self,estado):
        if estado == "ERRO": return estado
        
        estado = self.retirarVirgulas(estado)
        aux = ""
        for char in estado: 
            if aux.count(char) == 0:
                aux += char
        return ''.join(str(n) for n in sorted(list(aux)))
                    
    def retirarVirgulas(self,estado):
        """
        Retira as  virgulas do nome do estado para o metodo de determinizacao
        Por exemplo A,B,C vira ABC
        @param estado: string nome do estado que se quer retirar as virgulas
        @return: string nome do estado sem virgulas
        """
        #remove todas as virgulas do estado
        return ''.join([char if char != ','  else '' for char in estado])
                  
    def reconhecerSentenca(self,simbolo):
        """
        Verifica se a sentenca pertence ou nao a linguagem representada pelo automato
        @param simbolo: string sentenca que se quer reconhecer
        @return: True ou False
        """
	if self.ehDeterministico():
		estado = self.estadoInicial
		for caracter in simbolo:

		    if self.tabelaTransicao.get(estado).has_key(caracter):
			estado = self.tabelaTransicao.get(estado).get(caracter)
		    else:
			return False
	
		      
		if estado in self.estadosFinais:
		    return True
		return False       
	else:
		automato = Automato(self.tabelaTransicao, self.alfabeto, self.estados, self.estadoInicial, self.estadosFinais) 
		automato.determinizar()
		return automato.reconhecerSentenca(simbolo)
    
    def renomearAutomato(self):
        """
        Renomeia os estados do automato, deixando todos os nomes com apenas um caracter
        e atualiza todos os dados do automato
        """
        novosNomes = {}
        letras = map(chr, range(65, 91))

        #mapeia os novos nomes
        for estado in self.tabelaTransicao.keys():
            if len(estado) > 1:
                for i in letras:
                    if i not in self.estados and i not in novosNomes.values():
                        novosNomes[estado] = i
                        break
                    
        #substitui os novos nomes
        novasTransicoes = {}
        for estado in self.tabelaTransicao.keys():
            aux = {}
            
            trans = self.tabelaTransicao.get(estado)
            for t in trans.keys():
                if trans.get(t) in novosNomes.keys():
                    aux[t] = novosNomes.get(trans.get(t))
                else:
                    aux[t] = trans.get(t)
                    
            if estado in novosNomes.keys():
                novasTransicoes[novosNomes.get(estado)] = aux
            else:
                novasTransicoes[estado] = aux
                
        self.estados = novasTransicoes.keys()
        self.tabelaTransicao = novasTransicoes
        self.estadoInicial = (self.estadoInicial if self.estadoInicial not in novosNomes.keys() else novosNomes.get(self.estadoInicial))
        aux = set([])
        for i in self.estadosFinais:
            if i not in novosNomes.keys():
                aux.add(i)
            else:
                aux.add(novosNomes.get(i))
        self.estadosFinais = aux
        
    def __str__(self):
        print  "======= AUTOMATO ========"
        print "tabela transicao = ",
        print self.tabelaTransicao
        print "alfabeto = ",
        print  self.alfabeto
        print "estado inicial = ",
        print  self.estadoInicial
        print "estados = ",
        print  self.estados
        print "estados finais = ",
        print  self.estadosFinais
        print  "========================"
        return ""
            
    def removerEpsilonTransicao(self):
        """
        Remove as transicoes vazias do automato, em seguida determiniza
        e minimiza o automato
        """
        novasTransicoes = self.tabelaTransicao
        
        #para cada um dos estados do automato
        for i in range(len(self.estados)):

            for estado in self.estados:
                
                #pega todas as transicoes desse estado
                transicoes = self.tabelaTransicao.get(estado)
                
                for simbolo in transicoes.keys():
                    
                    #se essa transicao for vazia
                    if simbolo == "&":
                        
                        #vejo pra qual estado ele vai e copio as transicoes desse estado
                        estadosDestinos = transicoes.get(simbolo)
    
                        for estadoDestino in estadosDestinos:
                            if estadoDestino != ",":
                                #verificamos se o estado de destino eh final, pois entao esse tambem sera
                                if estadoDestino in self.estadosFinais:
                                    self.estadosFinais.add(estado)
                                    
                                #as novas transicoes serao as transicoes antigas (que adicionei aqui) mais as novas, que ainda vou adicionar
                                auxTrans = novasTransicoes.get(estado)               
            
                                #para cada transicao desse estado
                                transicaoDestino = novasTransicoes.get(estadoDestino)
                                for simbolo in transicaoDestino.keys():
                                    
                                    #caso ja exista um simbolo com essa transicao, eu concateno os dois
                                    if simbolo in auxTrans.keys():
                                        temp = transicaoDestino.get(simbolo)
                                        for aux in temp:
                                            if auxTrans.get(simbolo).count(aux) == 0 and aux != estado:
                                                aux = aux + "," + auxTrans.get(simbolo) 
                                                auxTrans.update( {simbolo: aux} )
                                        
                                    #caso nao exista um simbolo com essa transicao, eu simplesmente adiciono
                                    else:
                                        auxTrans.update( {simbolo:transicaoDestino.get(simbolo)} )
                                novasTransicoes[estado] = auxTrans
            #                else:
            #                    novasTransicoes[estado] = self.tabelaTransicao.get(estado)
            self.tabelaTransicao = novasTransicoes
            
        #agora ja tenho todas as transicoes copiadas, basta remover as epsilon transicoes
        for estado in novasTransicoes.keys():
            transicoes = novasTransicoes.get(estado)
            for simbolo in transicoes.keys():
                if simbolo == "&":
                    transicoes.pop(simbolo)
            novasTransicoes[estado] = transicoes
        
        #agora temos que achar o novo estado inicial e os novos estados finais
        self.tabelaTransicao = novasTransicoes
        self.determinizar()
        self.minimizarAFD()
                        
                        
                    
            
        
class ExcecaoMinimizarAutomatoNaoDeterministico(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr("Nao eh possivel minimizar um automato nao deterministico." + self.value)
            
                
