'''
Created on 18/05/2010

@author: patricia
'''
from Automatos.Automato import Automato

class Expressao():
    
    def __init__(self):
        self.possiveisNomes = map(chr, range(65, 91))
        
    def converterParaAF(self, expressaoRegular):
        """
        Converte a expressao regular passada para um automato finito com epsilon
        transicoes equivalente
        @param expressaoRegular: string
        @return Automato: automato finito com epsilon transicoes
        """
        
        #achou um bloco
        if expressaoRegular[0] == "(":
            
            i = 0

            #pegando o bloco inteiro
            while expressaoRegular[i] != ")":
                i += 1
            
            automato = self.converterParaAF(expressaoRegular[1:i])
            
            if i + 1 >= len(expressaoRegular):
                return automato
            
            #verifica se o proximo bloco eh *, + ou ?
            if expressaoRegular[i + 1] == "*":
                automato = self.fechamento(automato)
                i += 1
            elif expressaoRegular[i + 1] == "?":
                automato = self.opcional(automato)
                i += 1
            elif expressaoRegular[i + 1] == "+":
                automato = self.fechamentoPositivo(automato)
                i += 1

            i += 1
            if i >= len(expressaoRegular):
                return automato 
            
            #se nao for um dos dois, tem alguma coisa errada!!
            if  expressaoRegular[i] == ".":
                automato2 = self.converterParaAF(expressaoRegular[i+1:])
                return self.concatenacao(automato, automato2)

            elif expressaoRegular[i] == "|":
                automato2 = self.converterParaAF(expressaoRegular[i+1:])
                return self.uniao(automato, automato2)
            else:
                raise ExcecaoExpressaoInvalida("")
                
        if expressaoRegular[0] == "*" or expressaoRegular[0] == "?" or expressaoRegular[0] == "+":
            raise ExcecaoExpressaoInvalida("")
        
        #caso a expressao seja um simbolo, por exemplo, a
        else: 

            #manda montar o automato correspondente
            automato = self._montarAutomato(expressaoRegular[0])

            i = 1
            
            #caso ja tenha chegado no final da expressao
            if i >= len(expressaoRegular):
                return automato
             
            proximoSimbolo = expressaoRegular[i]

            if proximoSimbolo == "?":
                automato = self.opcional(automato)
                i += 1

            elif proximoSimbolo == "*":
                automato = self.fechamento(automato)
                i += 1
                
            elif proximoSimbolo == "+":
                automato = self.fechamentoPositivo(automato)
                i += 1
                
            if i >= len(expressaoRegular):
                return automato
            
            proximoSimbolo = expressaoRegular[i]
            
            #se nao for um dos dois, tem algo errado!!!
            if proximoSimbolo == ".":
                automato2 = self.converterParaAF(expressaoRegular[i+1:])
                return self.concatenacao(automato, automato2)

            elif proximoSimbolo == "|":
                automato2 = self.converterParaAF(expressaoRegular[i+1:])
                return self.uniao(automato, automato2)
            
            else:
                raise ExcecaoExpressaoInvalida("")
        
    def concatenacao(self, automato1, automato2):
        """
        Concatena os dois automatos passados usando epsilon transicoes
        @param automato1: automato que se quer concatenar ao segundo
        @param automato2: automato que vai se concatenar ao primeiro
        @return automato concatenado 
        """
        #verifica se os automatos nao tem estados com o mesmo nomes, caso tenham, renomeia
        if not self._verificarNomes(automato1, automato2):
            automato1, automato2 = self._renomearAutomatos(automato1, automato2)
        
        #cria uma nova tabela de transicao
        novaTabelaTransicao = automato1.tabelaTransicao
        
        #atualiza os antigos estados finais
        for estadoFinal in automato1.estadosFinais:
            # F -> aS .... estado final de A vai atraves de uma & transicao para o estado Inicial de B
            novaTrans = {"&": automato2.estadoInicial}

            transAntigas = novaTabelaTransicao[estadoFinal]         
               
            #verifica se essa transicao n era vazia, para nao perder as transicoes antigas
            for trans in transAntigas.keys():
                if trans == "&":
                    #caso ja tenha uma transicao por &, mantem a transicao e adiciona a nova transicao
                    novaTrans = {"&": transAntigas.get(trans) + "," + automato2.estadoInicial }
                if trans != "&":
                    novaTrans.update({trans:transAntigas.get(trans)})
            
            novaTabelaTransicao[estadoFinal] = novaTrans
            
        #para todos os outros estados, a gente simplesmente copia a transicao
        novaTabelaTransicao.update( automato2.tabelaTransicao )
        
        #monta o novo automato
        alfabeto = set( automato1.alfabeto ).union(set( automato2.alfabeto ))
        estados = novaTabelaTransicao.keys()
        estadoInicial = automato1.estadoInicial
        estadosFinais = automato2.estadosFinais
        return Automato(novaTabelaTransicao, alfabeto, estados, estadoInicial, estadosFinais)
    
    def fechamento(self, automato):
        """
        Faz o fechamento do automato passado usando epsilon transicoes
        @param automato: Automato que se quer fazer o fechamento
        @return: Automato 
        """
        novaTabelaTransicao = automato.tabelaTransicao
        estadoInicial, estadoFinal = self._acharNomePossiveisEstados(automato.estados)
        novaTabelaTransicao[estadoInicial] = {"&": automato.estadoInicial + "," + estadoFinal}
        novaTabelaTransicao[estadoFinal] = {"&":estadoInicial}
        
        #para cada um dos estados finais desse automato, atualiza o caminho
        for estado in automato.estadosFinais:
            
            #cria a nova transicao para o estado final
            novaTrans = {"&":estadoFinal}
            
            #agora precisamos verificar se nao estamos perdendo nenhuma transicao antiga
            transAntigas = novaTabelaTransicao[estado]         
            
            for trans in transAntigas.keys():
                if trans == "&":
                        #caso ja tenha uma transicao por &, mantem a transicao e adiciona a nova transicao
                        novaTrans = {"&": transAntigas.get(trans) + "," + estadoFinal }
                elif trans != "&":
                        novaTrans.update( { trans : transAntigas.get(trans) } )
                        
            novaTabelaTransicao[estado] = novaTrans
                
                
        estados = automato.estados + [estadoInicial] + [estadoFinal]
        estadosFinais = set([estadoFinal])
        return Automato(novaTabelaTransicao, automato.alfabeto, estados, estadoInicial, estadosFinais)
        
    def uniao(self, automato1, automato2):
        """
        Faz a uniao dos dois automatos passados usando epsilon transicoes
        @param automato1: automato que se quer unir ao segundo
        @param automato2: automato que se vai unir ao primeiro
        @return os dois automatos unidos 
        """
        #verifica se os automatos nao tem estados com o mesmo nomes, caso tenham, renomeia
        if not self._verificarNomes(automato1, automato2):
            automato1, automato2 = self._renomearAutomatos(automato1, automato2)
            
        #cria uma nova tabela de transicoes com todas as transicoes do automato 1 e 2
        novaTabelaTransicao = automato1.tabelaTransicao
        novaTabelaTransicao.update(automato2.tabelaTransicao)
        
        estados = automato1.estados + automato2.estados 

        #cria os dois novos estados inicial e final
        estadoInicial, estadoFinal = self._acharNomePossiveisEstados( estados )
        estados += [estadoInicial] + [estadoFinal]

        novaTabelaTransicao[estadoInicial] = {"&":automato1.estadoInicial + "," + automato2.estadoInicial}
        novaTabelaTransicao[estadoFinal] = {}
        
        #cria uma epsilon transicao de cada antigo estado final de A e B para o novo estado final
        for estadoFinalA in automato1.estadosFinais:
            
            #cria a nova transicao para o estado final
            novaTrans = {"&":estadoFinal}
            
            #agora precisamos verificar se nao estamos perdendo nenhuma transicao antiga
            transAntigas = novaTabelaTransicao[estadoFinalA]         
            
            for trans in transAntigas.keys():
                if trans == "&":
                        #caso ja tenha uma transicao por &, mantem a transicao e adiciona a nova transicao
                        novaTrans = {"&": transAntigas.get(trans) + "," + estadoFinal }
                elif trans != "&":
                        novaTrans.update( { trans : transAntigas.get(trans) } )
                        
            novaTabelaTransicao[estadoFinalA] = novaTrans
            
        for estadoFinalB in automato2.estadosFinais:
            #cria a nova transicao para o estado final
            novaTrans = {"&":estadoFinal}
            
            #agora precisamos verificar se nao estamos perdendo nenhuma transicao antiga
            transAntigas = novaTabelaTransicao[estadoFinalB]         
            
            for trans in transAntigas.keys():
                if trans == "&":
                        #caso ja tenha uma transicao por &, mantem a transicao e adiciona a nova transicao
                        novaTrans = {"&": transAntigas.get(trans) + "," + estadoFinal }
                elif trans != "&":
                        novaTrans.update( { trans : transAntigas.get(trans) } )
                        
            novaTabelaTransicao[estadoFinalB] = novaTrans
            
        alfabeto = automato1.alfabeto.union(automato2.alfabeto)
        
        #retorna o novo automato com todas as modificacoes criadas
        return Automato(novaTabelaTransicao, alfabeto, estados, estadoInicial, set([estadoFinal]))
        
    def opcional(self, automato):
        """
        Faz o ? do automato atraves de epsilon transicoes
        @param automato: Automato que se vai fazer a operacao de opcional
        @return: automato com a operacao realizada
        """
        novaTabelaTransicao = automato.tabelaTransicao
        estadoInicial, estadoFinal = self._acharNomePossiveisEstados(automato.estados)
        novaTabelaTransicao[estadoInicial] = {"&": automato.estadoInicial + "," + estadoFinal}
        novaTabelaTransicao[estadoFinal] = {}
        
        for estado in automato.estadosFinais:

            #cria a nova transicao para o estado final
            novaTrans = {"&":estadoFinal}
            
            #agora precisamos verificar se nao estamos perdendo nenhuma transicao antiga
            transAntigas = novaTabelaTransicao[estado]         
            
            for trans in transAntigas.keys():
                if trans == "&":
                        #caso ja tenha uma transicao por &, mantem a transicao e adiciona a nova transicao
                        novaTrans = {"&": transAntigas.get(trans) + "," + estadoFinal }
                elif trans != "&":
                        novaTrans.update( { trans : transAntigas.get(trans) } )
                        
            novaTabelaTransicao[estado] = novaTrans
                
                
        estados = automato.estados + [estadoInicial] + [estadoFinal]
        estadosFinais = set([estadoFinal])
        return Automato(novaTabelaTransicao, automato.alfabeto, estados, estadoInicial, estadosFinais)
        
    def fechamentoPositivo(self, automato):
        """
        Faz o fechamento positivo do automato passado atraves de epsilon transicoes
        @param automato: Automato que se quer realizar a operacao de fechamento positivo
        @return: Automato com a operacao de fechamento positivo realizada
        """
        novaTabelaTransicao = automato.tabelaTransicao
        estadoInicial, estadoFinal = self._acharNomePossiveisEstados(automato.estados)
        novaTabelaTransicao[estadoInicial] = {"&": automato.estadoInicial}
        novaTabelaTransicao[estadoFinal] = {"&":estadoInicial}
        
        for estado in automato.estadosFinais:

            #cria a nova transicao para o estado final
            novaTrans = {"&":estadoFinal}
            
            #agora precisamos verificar se nao estamos perdendo nenhuma transicao antiga
            transAntigas = novaTabelaTransicao[estado]         
            
            for trans in transAntigas.keys():
                if trans == "&":
                        #caso ja tenha uma transicao por &, mantem a transicao e adiciona a nova transicao
                        novaTrans = {"&": transAntigas.get(trans) + "," + estadoFinal }
                elif trans != "&":
                        novaTrans.update( { trans : transAntigas.get(trans) } )
                        
            novaTabelaTransicao[estado] = novaTrans
                
                
        estados = automato.estados + [estadoInicial] + [estadoFinal]
        estadosFinais = set([estadoFinal])
        return Automato(novaTabelaTransicao, automato.alfabeto, estados, estadoInicial, estadosFinais)
        
    def _verificarNomes(self, automatoA, automatoB):
        """
        Verifica se os dois automatos tem estados com os mesmo nomes
        @param AutomatoA: automato de referencia
        @param AutomatoB: automato que se verifica se tem os mesmos nomes que A
        @return True ou False
        """
        #pega os nomes de A e de B
        nomesA = set(automatoA.estados)
        nomesB = set(automatoB.estados)
        
        #retorna True caso nao tenham nomes iguais e False caso tenham
        return nomesA.intersection(nomesB) == set([]) 
    
    def _renomearAutomatos(self, automatoA, automatoB):
        """
        Renomeia os segundo automato com estados diferentes ao do primeiro
        @param AutomatoA: automato de referencia
        @param AutomatoB: automato que se vai alterar os nomes em relacao ao primeiro
        @return AutomatoA, AutomatoB sendo que o B teve seus valores alterados e o A
        se mantem intacto
        """
        possiveisNomes = map(chr, range(65, 91))
        estadosA = automatoA.estados
        novosNomes = {}

        #acha os substitutos de cada estado de B cujo nome ja existe em A
        for estadoB in automatoB.estados:
            if estadoB in estadosA:
                for letra in possiveisNomes:
                    if letra not in estadosA[:] and letra not in novosNomes.values():
                        novosNomes[estadoB] = letra
            else:
                novosNomes[estadoB] = estadoB

        novaTabelaTransicao = {}
        for estado in automatoB.tabelaTransicao.keys():
            transicao = automatoB.tabelaTransicao.get(estado)
            aux = {}
            for alfabeto in transicao.keys():
                valor = transicao.get(alfabeto)
                nm = ""
                for i in valor:
                    if i != ",":
                        nm +=  novosNomes[i] + ","
                aux[alfabeto] = nm[:-1]
            
            novaTabelaTransicao[ novosNomes[estado] ] = aux

        #criando os novos dados do automato
        estadoInicial = novosNomes[ automatoB.estadoInicial ]
        estados = novosNomes.values()
        estadosFinais = set([novosNomes[estado] for estado in automatoB.estadosFinais])
        
        #montando o novo automato
        novoAutomatoB = Automato(novaTabelaTransicao, automatoB.alfabeto, estados, estadoInicial, estadosFinais)
        return automatoA, novoAutomatoB   
        
    def _acharNomePossiveisEstados(self, estados):
        """
        Acha os nomes possiveis (que nao foram utilizados ainda) para o
        estado inicial e o estado final com base nos nomes dos estados
        @param estados: nomes dos estados que vai se usar de base para achar
        os outros nomes
        @return: estadoInicial, estadoFinal nome dos estados inicial e final
        """
        estadoInicial = None
        estadoFinal = None

        #de frente pra tras
        for letra in self.possiveisNomes:
            if letra not in estados:
                estadoInicial = letra
                self.possiveisNomes.remove(letra)
                break
        
        #de tras pra frente
        self.possiveisNomes.reverse()
        for letra in self.possiveisNomes:
            if letra not in estados and letra != estadoInicial:
                estadoFinal = letra
                self.possiveisNomes.remove(letra)
                break
            
        return estadoInicial, estadoFinal
            
    def _montarAutomato(self, simbolo):
        """
        Monta o automato referente ao simbolo passado
        @param simbolo: simbolo que se quer montar o automato
        @return Automato: automato montado
        """
        a = self.possiveisNomes[0]
        b = self.possiveisNomes[1]
        self.possiveisNomes.remove(a)
        self.possiveisNomes.remove(b)
        estados = [a,b]
        estadoInicial = a
        estadosFinais = set([b])
        tabelaTransicao = {a:{simbolo:b}, b:{}}
        alfabeto = set([simbolo])

        return Automato(tabelaTransicao, alfabeto, estados, estadoInicial, estadosFinais)
        
        
class ExcecaoExpressaoInvalida(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr("Expressao entrada eh invalida. " + self.value)