'''
Created on 18/05/2010

@author: patricia
'''
from Producao import Producao
import re

class Gramatica(object):
    
    def __init__(self,producaoInicial,naoTerminais, terminais ,producoes):
        
        if producaoInicial == None or naoTerminais == None or terminais == None or producoes == None:
            raise ExcecaoConstruirGramatica
        
        self.producaoInicial = producaoInicial    #producao inicial da gramatica
        self.producoes = producoes                  #dicionario de producoes
        self.terminais = terminais                      #conjunto de terminais
        self.naoTerminais = naoTerminais           #conjunto de nao terminais
        
    
                
    def obterProducao(self,alfa):
        """
        Retorna a producao que tem por alfa o alfa passado
        @param alfa: string alfa que se que a producao correspondente
        @return Producao: producao que tem por alfa o alfa pasado
        """
        for producao in self.producoes:
            if producao.obterAlfa() == alfa:
                return producao            
    
    def gerarSentencas(self,n):
        """
        Gera as sentencas de tamanho 1 ate n
        @param n: integer tamanho das sentencas que se quer gerar
        @return: conjunto de sentencas geradas
        """
        sentencasTerminadas = set([])
        sentencasPorTerminar = set([])
        naoMaisDerivaveis = set([])
        
        #para cada um dos betas dessa producao 
        for beta in self.producaoInicial.obterListaBetas():
            if len(beta) == 1:
                sentencasTerminadas.add(beta)
            elif len(beta) == 2:
                sentencasPorTerminar.add(beta)

        #depois de incializar as duas sentencas, comeca a derivar as possiveis
        while len(sentencasPorTerminar) > 0:

            #pega uma das sentencas por terminar
            sentenca = sentencasPorTerminar.pop()
            naoMaisDerivaveis.add(sentenca)

            #para cada um dos simbolos dessa sentenca
            for indice in range(len(sentenca)):
                simbolo = sentenca[indice]
               
                #se for um simbolo nao terminal
                if simbolo in self.naoTerminais:
                    
                    #pega a producao que corresponde a esse simbolo e todas as suas possiveis transicoes
                    producao = self.obterProducao(simbolo)
                    transPossiveis = producao.obterListaBetas()
                    
                    #para cada uma de suas transicoes
                    for trans in transPossiveis:
                        
                        #verifica se aplicando essa transicao a sentenca ainda esta dentro do tamanho desejado (-1 pq tira o nao terminal que
                        #pode ser substituido por um terminal )
                        if len(sentenca) - 2 + len(trans) <= n:
                            
                            #faz a substituicao
                            nova = sentenca.replace(simbolo, trans)
                            terminada = True
                            
                            if nova != "&":
                                nova = nova.replace('&','')

                            #verifica se essa sentenca ainda pode ser derivada
                            for s in nova:
                                if s in self.naoTerminais:
                                    terminada = False

                            if terminada and len(nova)<=n:
                                    sentencasTerminadas.add(nova)

                            elif not terminada and nova not in naoMaisDerivaveis:
                                sentencasPorTerminar.add(nova)
        
        return sentencasTerminadas
                                
class ExcecaoConstruirGramatica(Exception):
    def __str__(self):
        return repr("Impossivel criar Gramatica")                  
            