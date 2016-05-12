SIMBOLO_SEPARADOR = "|"
class Producao:

    def __init__(self,alfa,beta):
        
        #define alfa e beta como variaveis privadas
        self.__alfa = alfa
        self.__beta = beta
        
    def obterAlfa(self):
        return self.__alfa
    
    def obterBeta(self):
        return self.__beta
    
    def obterListaBetas(self):
        return self.__beta.split(SIMBOLO_SEPARADOR)
    
    def obterPossiveisTransicoes(self,simbolo):
        possiveisTransicoes = []
        for transicao in self.obterListaBetas():
            if transicao[0] == simbolo:
                possiveisTransicoes.append(transicao)
        return possiveisTransicoes
    
    def __str__(self):
        return self.obterAlfa() + "->" + self.obterBeta()
    
#    def __cmp__(self, producao):
#        if self.__alfa == producao.obterAlfa() and self.__beta == producao.obterBeta():
#            return True
#        return False