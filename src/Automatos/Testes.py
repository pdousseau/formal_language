'''
Created on 22/05/2010

@author: patricia
'''

import unittest
from Automato import Automato

class Testes(unittest.TestCase):
    
    
    def testeDeterminar1(self):
                        
        alfabeto = ("a","b")
        estados = ("S","A","B","C")
        estadosFinais = ("C")
        estadoInicial = "S"
        tab = {"S":{"a":"S,A", "b":"S"}, 
               "A":{"b":"B"}, 
               "B":{"b":"C"}, 
               "C":{} 
                }
        
        automato = Automato(tab,alfabeto, estados, estadoInicial, estadosFinais)
        automato.determinarAFND()
        
        resultado = {"S":{"a":"AS", "b":"S"}, 
                     "AS":{"a":"AS","b":"BS"}, 
                     "BS":{"a": "AS","b":"CS"}, 
                     "CS":{"a":"AS","b":"S"}  }
        self.assertEqual(automato.tabelaTransicao,resultado)
        self.assertEqual(automato.estadoInicial,"S")
        self.assertEqual(automato.estadosFinais, set(["CS"]))
        automato.renomearAutomato()
        automato.converterParaGramatica()
        
        
    
    def testeDeterminar2(self):
        alfabeto = ("a","b","c")
        estados = ("S","A","B","C","F")
        estadosFinais = ("S","F")
        estadoInicial = "S"
        tab = {"S":{"a":"A", "b":"B,F","c":"SF"},
        "A":{"a":"S,F","b":"C", "c":"A"},
        "B":{"a":"A", "c":"B,S,F"},
        "C":{"a":"S,F", "c":"A,C"},
        "F":{},
        }
        
        automato = Automato(tab,alfabeto, estados, estadoInicial, estadosFinais)
        automato.determinarAFND()
        resultado = {"S":{"a":"A","b": "BF", "c":"FS"} ,
                     "BF":{"a":"A","b":'',"c":"BFS"},
                     "FS":{"a":"A","b":"BF","c":"FS"},
                     "BFS":{"a":"A","b":"BF","c":"BFS"},
                     "A":{"a":"FS","b":"C","c":"A"},
                     "C":{"a":"FS","b":'',"c":"AC"},
                     "AC":{"a":"FS","b":"C","c":"AC"}
                     }
        self.assertEqual(automato.tabelaTransicao,resultado)
        self.assertEqual(automato.estadoInicial,"S")
        self.assertEqual(automato.estadosFinais,set(["BF","FS","BFS","S"]))
        
    def testeDeterminar3(self):
        estadoInicial = "S"
        alfabeto = (0,1)
        estados = ("S","A","B","C","D","E")
        estadosFinais = ("E")
        tab = {"S":{0:"A,D",1:"E"},
               "A":{0:"A,B",1:"C,E"},
               "B":{0:"B"},
               "C":{0:"A,B"},
               "D":{0:"B,D",1:"C"},
               "E":{0:"E",1:"E"}
        }
        automato = Automato(tab,alfabeto, estados, estadoInicial, estadosFinais)
        automato.determinarAFND()
        resultado = {
                     "S":{0:"AD",1:"E"},
                     "AD":{0:"ABD",1:"CE"},
                     "E":{0:"E",1:"E"},
                     "ABD":{0:"ABD",1:"CE"},
                     "CE":{0:"ABE",1:"E"},
                     "ABE":{0:"ABE",1:"CE"}
                     }
        self.assertEqual(automato.tabelaTransicao,resultado)
        self.assertEqual(automato.estadoInicial,"S")
        self.assertEqual(automato.estadosFinais,set(["E","CE","ABE"]))
    
    def testeMinimizar1(self):
        tab = {
       "A":{"a":"G", "b":"B"},
       "B":{"a":"F", "b":"E"},
       "C":{"a":"C", "b":"G"},
       "D":{"a":"A", "b":"H"},
       "E":{"a":"E", "b":"A"},
       "F":{"a":"B", "b":"C"},
       "G":{"a":"G", "b":"F"},
       "H":{"a":"H", "b":"D"},
       }
        estadosFinais = ("A","D","G")
        alfabeto = ("a","b")
        estados = ("A","B","C","D","E","F","G","H")
        estadoInicial = "A"
        automato = Automato(tab,alfabeto, estados, estadoInicial, estadosFinais)
        automato.minimizarAFD()
        
        resultado = {
                     "AG":{"a":"AG","b":"BF"},
                     "BF":{"a":"BF","b":"CE"},
                     "CE":{"a":"CE","b":"AG"}
        }
        
        self.assertEqual(automato.tabelaTransicao, resultado)
        self.assertEqual(automato.estadoInicial,"AG")
        self.assertEqual(automato.estadosFinais,set(["AG"]))
        self.assertTrue(automato.reconhecerSentenca("aaa"))
        self.assertFalse(automato.reconhecerSentenca("abaa"))
        
    def testeMinimizar2(self):
        tab = {
               "S":{"a":"A", "b":"B", "c":"D"},
               "A":{"a":"D", "b":"C", "c":"A"},
               "B":{"a":"A", "c":"E"},
               "C":{"a":"D", "c":"F"},
               "D":{"a":"A", "b":"B", "c":"D"},
               "E":{"a":"A", "b":"B", "c":"E"},
               "F":{"a":"D", "b":"C", "c":"F"}
               }
        
        estadosFinais = ("S","B","D","E")
        estadoInicial = "S"
        estados = ("S","A","B","C","D","E","F")
        alfabeto = ("a","b","c")
        automato = Automato(tab,alfabeto, estados, estadoInicial, estadosFinais)
        automato.minimizarAFD()
        resultado = {
                     "DES":{"a":"AF","b":"B","c":"DES"},
                     "AF":{"a":"DES","b":"C","c":"AF"},
                     "C":{"a":"DES", "b":"ERRO", "c":"AF"},
                     "B":{"a":"AF", "b":"ERRO", "c":"DES"},
                     "ERRO":{"a":"ERRO", "b":"ERRO", "c":"ERRO"}
                     }
        self.assertEqual(automato.tabelaTransicao, resultado)
        self.assertEqual(automato.estadoInicial,"DES")
        self.assertEqual(automato.estadosFinais,set(["DES","B"]))
        self.assertTrue(automato.reconhecerSentenca("cbaa"))
        self.assertFalse(automato.reconhecerSentenca("bcca"))
        
    def testeMinimizar3(self):
        tab = {
               "S":{"a":"A", "b":"B"},
               "A":{"a":"C"},
               "B":{"b":"D"},
               "C":{"a":"C", "b":"C"},
               "D":{"a":"D", "b":"D"}
               }
        alfabeto = ("a","b")
        estadoInicial = "S"
        estadosFinais = ("C","D")
        estados = ("S","A","B","C","D")
        automato = Automato(tab,alfabeto, estados, estadoInicial, estadosFinais)
        automato.minimizarAFD()
        resultado = {
                     "S":{"a":"A", "b":"B"},
                     "A":{"a":"CD", "b":"ERRO"},
                     "B":{"a":"ERRO", "b":"CD"},
                     "CD":{"a":"CD", "b":"CD"},
                     "ERRO":{"a":"ERRO","b":"ERRO"}
                     }
        self.assertEqual(automato.tabelaTransicao,resultado)
        
        print "--------------------"
        print automato.tabelaTransicao
        automato.renomearAutomato()
        print automato.estadosFinais
        print automato.estadoInicial

if(__name__ == "__main__"):  
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Testes))
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    
