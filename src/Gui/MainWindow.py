from PyQt4.QtGui import QMainWindow,QListWidgetItem, QMessageBox, QTableWidgetItem, QInputDialog,QLineEdit, QFileDialog
from Ui_MainWindow import Ui_MainWindow
from Gramaticas.Producao import Producao
from Gramaticas.Gramatica import Gramatica, ExcecaoConstruirGramatica
from Automatos.Automato import Automato, ExcecaoMinimizarAutomatoNaoDeterministico
from Expressao.Expressao import Expressao, ExcecaoExpressaoInvalida
import pickle, random

SIMBOLO_SEPARADOR_TRANSICAO = "|"
SIMBOLO_SEPARADOR_PRODUCAO = "->"
DIRETORIO_GRAMATICAS = "persistencia/Gramaticas/"
DIRETORIO_AUTOMATOS = "persistencia/Automatos/"



class MainWindow (QMainWindow, Ui_MainWindow):
    """
    Janela grafica do programa, que chama e configura os metodos
    dos automatos e das gramaticas
    """    
    
    def __init__(self, parent=None):
        '''
        inicializa os dados da gramatica e do automato atuais
        '''
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self._infoGramaticaAtual = { 
                                     "ProducaoInicial" : None,
                                     "NaoTerminais" : set([]),
                                     "Terminais" : set([]),
                                     "Producoes" : []
                                     }
        
        self._infoAutomatoAtual = {
                                    "EstadoInicial" : None,
                                    "EstadosFinais" : set([]),
                                    "Alfabeto" : set([]),
                                    "Estados" : set([]),
                                    "TabelaTransicao" : {}
                                    }
        
    def adicionarProducao(self):
        '''
        adiciona a producao entrada na caixa de producoes na lista de producao
        apenas se ela for valida
        Gera uma excecao caso a producao nao seja valida
        '''
        try:
            
            #pega a producao entrada pelo usuario e remove os espacos em branco
            producao = self.caixaProducoes.text().remove(" ")

            #verifica se tem epsilon, caso tenha, tem que estar na producao inicial e nao deve possuir recursao
            if str(producao).count("&") > 0 and (self.listaProducoes.count() > 0 or str(producao).count(str(producao)[0]) >= 2 ):
                raise ExcecaoAdicionarProducao("Producao invalida. So eh permitido & na producao inicial e sem recursao")

            #verifica se a producao atende os padroes das gramaticas regulares
            if self._verificarProducao(producao):
                p = QListWidgetItem(producao)
                self.listaProducoes.addItem(p)
                self.caixaProducoes.setText("")
            
        except ExcecaoAdicionarProducao as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)

    def deletarProducao(self):
        '''
        Deleta a producao selecionada pelo usuario na lista de producoes ja aceitas
        e remove o alfa dessa producao da lista de nao terminais
        '''
        linha = self.listaProducoes.currentRow()
        item = self.listaProducoes.takeItem(linha)
        nt = self._infoGramaticaAtual["NaoTerminais"]
        self._infoGramaticaAtual["NaoTerminais"] = nt.difference(str(item.text())[0])
        
    def converterGRparaAF(self):
        """
        Converte a gramatica entrada pelo usuario em um automato finito
        primeiro monta a gramatica pegandos os dados que estao na lista de producao
        depois manda converter e mostrar o automato resultante
        """
        try:
            self._limparAutomatoResultante()
            gramatica = self._montarGramatica()
            if gramatica is not None:
                automato = self._converterGRparaAF(gramatica)
                self._mostrarAutomato(automato)
        except ExcecaoImpossivelMontarGramatica as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
        
    def novaGramatica(self):
        """
        Limpa todas as caixas e listas e reinicializa as variaveis para poder 
        criar uma nova gramatica
        """
        self._limparListaSentencas()
        self._limparProducoes()
        self._limparCaixasGramatica()
        self._infoGramaticaAtual["NaoTerminais"] = set([])
        
    def novoAutomato(self):
        """
        Limpa todas as caixas, listas e tabelas e tambem reinicializa
        as variaveis para poder criar um novo automato
        """
        self._infoAutomatoAtual["EstadoInicial"] = None
        self._infoAutomatoAtual["EstadosFinais"] = set([])
        self._infoAutomatoAtual["Alfabeto"] = set([])
        self._infoAutomatoAtual["Estados"] = set([])
        self._infoAutomatoAtual["TabelaTransicao"] = {}
        self._limparAutomatoResultante()
        self._limparEstados()
        self._limparAlfabeto()
        self._limparCaixasAutomato()
        
    def gerarSentencas(self):
        """
        Gera as sentencas de tamanho n utilizando a gramatica
        passada pelo usuario
        """
        
        try:
            #pega o valor de n (tamanho da sentenca)
            n = int(self.caixaTamanhoProducoes.text())
            if n <= 0:
                QMessageBox.warning(self,"Erro","Entre com um numero positivo maior que zero.", QMessageBox.Ok)
                return
        
            #limpa a lista de sentencas anteriores, monta a gramatica e gera as sentencas
            self._limparListaSentencas()
            gramatica = self._montarGramatica()
            sentencas = gramatica.gerarSentencas(n)
            
            #popula a lista de sentencas
            for sentenca in sentencas:
                self.listaSentencas.addItem( QListWidgetItem(str(sentenca))  )
                
        except ExcecaoConstruirGramatica:
            QMessageBox.warning(self,"Erro","Impossivel construir a gramatica", QMessageBox.Ok)
        except ValueError:
            QMessageBox.warning(self,"Erro","Entre com um numero positivo maior que zero.", QMessageBox.Ok)

    def adicionarEstado(self):
        """
        Adiciona o estado passado na caixa de estados pelo usuario
        na lista de estados e nos dados do automato
        Apenas insere o estado caso ele seja valido
        """
        estado = str(self.caixaEstado.text())
        
        #verifica se eh uma letra maiuscula que ainda nao foi utilizada
        if estado != estado.upper() or estado == "":
            QMessageBox.warning(self,"Erro","O estado deve ser uma letra maiuscula.", QMessageBox.Ok)
            return
        if estado in self._infoAutomatoAtual["Estados"]:
            QMessageBox.warning(self,"Erro","Esse estado ja foi inserido.", QMessageBox.Ok)
            return
        
        estados = self._infoAutomatoAtual["Estados"]
        self._infoAutomatoAtual["Estados"] = estados.union(estado)
        
        #monta o nome do estado com * e -> para poder colocar na lista de estados e na tabela de transicao
        nomeEstado = estado
        if self.cbFinal.isChecked():
            estadosFinais = self._infoAutomatoAtual["EstadosFinais"]
            self._infoAutomatoAtual["EstadosFinais"] = estadosFinais.union(estado)
            nomeEstado = "*" + nomeEstado

        if self.cbInicial.isChecked():
            estadoInicial = self._infoAutomatoAtual["EstadoInicial"]
            
            #caso seja um estado inicial, verifica se eh o primeiro inserido, caso nao seja, substitui o anterior
            if estadoInicial != None:
                QMessageBox.warning(self,"Atencao","Estado inicial antigo ("+estadoInicial+") substituido por ("+estado+")!", QMessageBox.Ok)

                #substitui o antigo na tabela de transicao
                for i in range(self.tabelaTransicoes.columnCount()):
                    if str(self.tabelaTransicoes.takeVerticalHeaderItem(i).text()) == "->" + estadoInicial or str(self.tabelaTransicoes.takeVerticalHeaderItem(i).text()) == "->*" + estadoInicial:
                        self.tabelaTransicoes.setVerticalHeaderItem(i,QTableWidgetItem(estadoInicial.replace("->","")))
                        
            self._infoAutomatoAtual["EstadoInicial"] = estado
            nomeEstado = "->" + nomeEstado
            
        #adiciona na lista de estados e na tabela de transicao
        self.listaEstados.addItem(nomeEstado)
        n = self.tabelaTransicoes.rowCount()
        self.tabelaTransicoes.setRowCount(n+1)
        self.tabelaTransicoes.setVerticalHeaderItem(n,QTableWidgetItem(nomeEstado))
        self.caixaEstado.setText("")
        self.cbFinal.setChecked(False)
        self.cbInicial.setChecked(False)
            
    def adicionarAlfabeto(self):
        """
        Adiciona um letra do alfabeto entrada pelo usuario na lista de alfabeto 
        e nas informacoes do automato atual
        Apenas insere o simbolo na lista do alfabeto caso ele seja valido
        """
        
        #pega o alfabeto entrado
        alfabeto = str(self.caixaAlfabeto.text())
        
        #verifica se eh minusculo e se ainda nao foi utilizado
        if alfabeto != alfabeto.lower() or alfabeto == "":
            QMessageBox.warning(self,"Erro","O alfabeto deve ser uma letra minuscula.", QMessageBox.Ok)
            return
        if alfabeto in self._infoAutomatoAtual["Alfabeto"]:
            QMessageBox.warning(self,"Erro","Esse simbolo ja foi inserido.", QMessageBox.Ok)
            return
        
        #adiciona nas informacoes do automato atual, na tabela de transicao e na lista de alfabetos
        n = self.tabelaTransicoes.columnCount()
        self.tabelaTransicoes.setColumnCount(n+1)
        self.tabelaTransicoes.setHorizontalHeaderItem(n,QTableWidgetItem(alfabeto))
        letras = self._infoAutomatoAtual["Alfabeto"]
        self._infoAutomatoAtual["Alfabeto"] = letras.union(alfabeto)
        self.listaAlfabeto.addItem(alfabeto)
        self.caixaAlfabeto.setText("")
    
    def deletarEstado(self):
        """
        Deleta o estado selecionado pelo usuario e remove
        as referencias a esse estado das informacoes do 
        automato atual
        """
        
        #pega o estado que o usuario deseja remover
        estado = str(self.listaEstados.currentText())
        
        #verifica se existe algum estado para remover
        if estado != "":
            indice = self.listaEstados.currentIndex()
            self.listaEstados.removeItem(indice)
    
            #agora deleta a linha desse estado
            for indice in range(self.tabelaTransicoes.rowCount()):
                if self.tabelaTransicoes.verticalHeaderItem(indice).text() == estado:
                    self.tabelaTransicoes.removeRow(indice)
                    break
    
            #formata o nome do estado e remove ele das informacoes do automato
            estado = estado.replace('*','')
            estado = estado.replace('->','')          
            estados = self._infoAutomatoAtual["Estados"]
            estados.remove(estado)
            self._infoAutomatoAtual["Estados"] = estados
            
            #caso ele esteja na lista de estados finais, remove
            if estado in self._infoAutomatoAtual["EstadosFinais"]:
                estadosFinais = self._infoAutomatoAtual["EstadosFinais"]
                estadosFinais.discard(estado)
                self._infoAutomatoAtual["EstadosFinais"] = estadosFinais
            
            #caso ele fosse um estado inicial, remove
            if estado == self._infoAutomatoAtual["EstadoInicial"]:
                self._infoAutomatoAtual["EstadoInicial"] = None
        
    def deletarAlfabeto(self):
        """
        Retira da lista de alfabeto e das informacoes do automato
        o simbolo selecionado pelo usuario
        """
        #pega o simbolo que o usuario deseja deletar
        alfabeto = str(self.listaAlfabeto.currentText())
        
        #verifica se esse simbolo realmente existe
        if alfabeto != "":
            indice = self.listaAlfabeto.currentIndex()
            self.listaAlfabeto.removeItem(indice)
            letras = self._infoAutomatoAtual["Alfabeto"]
            letras.remove(alfabeto)
            self._infoAutomatoAtual["Alfabeto"] = letras
            
            #agora deleta a coluna dessa letra
            for indice in range(self.tabelaTransicoes.columnCount()):
    
                if self.tabelaTransicoes.horizontalHeaderItem(indice).text() == alfabeto:
                    self.tabelaTransicoes.removeColumn(indice)
                    return
        
    def determinizarAutomato(self):
        """
        Determiniza o automato especificado
        na tabela de transicoes
        """
        try:
            automato = self._montarAutomato()
            if automato is not None:
                automato.determinizar()
                self._mostrarAutomato(automato)
        except ExcecaoImpossivelMontarAutomato as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
    
    def minimizarAutomato(self):
        """
        Minimiza o automato especificado na tabela de transicoes
        caso o automato nao esteja determinizado, a excecao
        gerada eh tratada
        """
        try:
            automato = self._montarAutomato()
            automato.minimizarAFD()
            self._mostrarAutomato(automato)
                
        except ExcecaoMinimizarAutomatoNaoDeterministico as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
        except ExcecaoImpossivelMontarAutomato as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
            
    def converterERparaAF(self):
        """
        Converte a expressao regular passada pelo usuario em um automato
        deterministico e minimo
        Trata uma excecao caso a gramatica passada seja invalida
        """
        er = str( self.caixaER.text().remove("") )
        
        expressaoRegular = Expressao()
        try:
            automato = expressaoRegular.converterParaAF(er)
            automato.removerEpsilonTransicao()
            self._mostrarAutomato(automato)
        except ExcecaoExpressaoInvalida as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
        
    def salvarAutomato(self):
        """
        Salva o automato caso ele seja valido em um arquivo
        na pasta especificada em DIRETORIO_AUTOMATOS
        tendo por default um nome no formato automato[NumeroQualquer]
        podendo ser alterado por um nome escolhido pelo usuario
        """
        try:
            automato = self._montarAutomato()
            
            #gera um numero qualquer para montar o nome do automato
            x = int(random.random()*1000)
            
            #retorna uma tupla (nomeArquivo, true/false)
            nomeArq = QInputDialog.getText(self,"Nome do arquivo", "Qual o nome do automato?", QLineEdit.Normal, "Automato" + str(x))
            if nomeArq[1]:
                pickle.dump(automato, file(DIRETORIO_AUTOMATOS  + str(nomeArq[0]), 'w'))
                QMessageBox.information(self,"Automato salvo","Automato salvo com sucesso!")
                
        except ExcecaoImpossivelMontarAutomato as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
        
    def salvarGramatica(self): 
        """
        Salva a gramatica caso ela seja valida em um arquivo
        na pasta especificada em DIRETORIO_GRAMATICAS
        tendo por default um nome no formato gramatica[NumeroQualquer]
        podendo ser alterado por um nome escolhido pelo usuario
        """
        try: 
            gramatica = self._montarGramatica()
            
            #numero qualquer para gerar o nome da gramatica
            x = int(random.random()*1000)
            
            #retorna uma tupla (nomeArquivo, true/false)
            nomeArq = QInputDialog.getText(self,"Nome do arquivo", "Qual o nome do gramatica?", QLineEdit.Normal, "Gramatica" + str(x))
            if nomeArq[1]:
                pickle.dump(gramatica, file(DIRETORIO_GRAMATICAS  + str(nomeArq[0]), 'w'))
                QMessageBox.information(self,"Gramatica salva","Gramatica salva com sucesso!")
                
        except ExcecaoImpossivelMontarGramatica as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
            
    def carregarAutomato(self):
        """
        Carrega um automato de um arquivo e monta e mostra o 
        automato na tabela de transicao
        """
        nomeArquivo = str(QFileDialog.getOpenFileName(self, 'Abrir automato',DIRETORIO_AUTOMATOS,""))    
        arq = file(nomeArquivo)
        automato = pickle.load(arq)
        arq.close()
        if automato is not None:
            self._mostrarAutomato(automato)
        
    def carregarGramatica(self):
        """
        Carrega um arquivo contendo uma gramatica e monta
        e mostra a gramatica na lista de producoes
        """
        nomeArquivo = str(QFileDialog.getOpenFileName(self, 'Abrir gramatica',DIRETORIO_GRAMATICAS,""))    
        arq = file(nomeArquivo)
        gramatica = pickle.load(arq)
        arq.close()
        if gramatica is not None:
            self._mostrarGramatica(gramatica)
            
    def reconhecerSentenca(self):
        """
        Verifica se o automato em questao reconhece uma sentenca especifica ou nao
        """
        try:
            automato = self._montarAutomato()
            sentenca = str(self.caixaSentenca.text())
            reconheceu = automato.reconhecerSentenca(sentenca)
            if reconheceu:
                QMessageBox.information(self,"Reconhecimento","A sentenca " + sentenca + " pertence a linguagem!")
            else:
                QMessageBox.information(self,"Reconhecimento","A sentenca " + sentenca + " nao pertence a linguagem!")
                
        except ExcecaoImpossivelMontarAutomato as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
    
    def converterAFparaGR(self):
        """
        Converte um automato finito que esteja corretamente
        especificado para uma gramatica regular e mostra essa
        gramatica na lista de producoes
        Verifica se o automato esta corretamente especificado
        """
        try:
            self._limparProducoes()
            automato = self._montarAutomato()
            gramatica = self._converterAFparaGR(automato)
            self._mostrarGramatica(gramatica)
            
        except ExcecaoImpossivelMontarAutomato as mensagem:
            QMessageBox.warning(self,"Erro", str(mensagem), QMessageBox.Ok)
               
    def _limparAutomatoResultante(self):
        """
        Limpa a tabela de transicao que contem
        o automato resultante
        NAO DELETA as informacoes do automato, apensar apaga
        o automato visualmente
        """
        for _ in range(self.tabelaTransicoes.rowCount()):
            self.tabelaTransicoes.removeRow(0)
            
        for _ in range(self.tabelaTransicoes.columnCount()):
            self.tabelaTransicoes.removeColumn(0)
        
    def _atualizarAutomato(self, automato):
        """
        Atualiza as informacoes do automato usando os 
        dados do automato passado como paramentro
        """
        self._infoAutomatoAtual["EstadoInicial"] = automato.estadoInicial
        self._infoAutomatoAtual["EstadosFinais"] = automato.estadosFinais
        self._infoAutomatoAtual["Alfabeto"] = automato.alfabeto
        self._infoAutomatoAtual["Estados"] = automato.estados
        self._infoAutomatoAtual["TabelaTransicao"] = automato.tabelaTransicao  
        
    def _atualizarGramatica(self, gramatica):
        """
        Atualiza as informacoes da gramatica usando os 
        dados da gramatica passada como paramentro
        """
        self._infoGramaticaAtual["ProducaoInicial"] = gramatica.producaoInicial
        self._infoGramaticaAtual["NaoTerminais"] = gramatica.naoTerminais
        self._infoGramaticaAtual["Terminais"] = gramatica.terminais
        self._infoGramaticaAtual["Producoes"] = gramatica.producoes
        
    def _mostrarAutomato(self, automato):
        """
        Mostra o automato passado (e ja corretamente especificado)
        na tabela de transicao
        Tambem popula a lista de estados e a lista de simbolos do alfabeto
        """
        #limpandos os dados do automato anterior
        self._limparCaixasAutomato()
        self._limparAlfabeto()
        self._limparEstados()
        self._limparAutomatoResultante()
        
        self._atualizarAutomato(automato)
       
        tabelaTransicao = automato.tabelaTransicao
       
        #pega os simbolos de transicao e ordena
        alfabeto = ([letra for letra in automato.alfabeto])
        alfabeto.sort()
        
        #popula a lista de simbolos do alfabeto
        for letra in alfabeto:
            n = self.tabelaTransicoes.columnCount()
            self.tabelaTransicoes.setColumnCount(n+1)
            self.tabelaTransicoes.setHorizontalHeaderItem(n,QTableWidgetItem(letra))
            self.listaAlfabeto.addItem(letra)
        
        #para cada um dos estados do automato
        linha = 0
        n = len(tabelaTransicao.keys()) 
        self.tabelaTransicoes.setRowCount( n )
        
        #popula a lista de estados
        for estado in tabelaTransicao.keys():
            transicoes = tabelaTransicao.get(estado)
            
            if estado == self._infoAutomatoAtual["EstadoInicial"] and estado in self._infoAutomatoAtual["EstadosFinais"]: 
                estado = "*->" + estado
            elif estado == self._infoAutomatoAtual["EstadoInicial"]:
                estado = "->" + estado
            elif estado in self._infoAutomatoAtual["EstadosFinais"]: 
                estado = "*" + estado
            
            self.tabelaTransicoes.setVerticalHeaderItem(linha,QTableWidgetItem(estado))
            self.listaEstados.addItem(estado)
            coluna = 0

            for letra in transicoes.keys():
                simbolo = transicoes.get(letra)

                for i in range(len(alfabeto)):
                    if alfabeto[i] == letra:
                        coluna = i
                        self.tabelaTransicoes.setItem(linha,coluna,QTableWidgetItem(simbolo))
                
                
            linha += 1
            
    def _verificarProducao(self, producao):
        """
        Verifica se a producao passada eh valida segundo
        as especificados das gramaticas regulares
        Retorna True ou lanca uma excecao contendo a explicacao
        do porque a producao nao foi aceita 
        """
        #valores possiveis de serem usados na producao
        maiusculas = map(chr, range(65, 91))
        minusculas = map(chr, range(97, 123))
        numeros = map(chr, range(48, 57))
        numeros.append("&")
        
        p = producao.split(SIMBOLO_SEPARADOR_PRODUCAO)

        #se o resultado for maior que 2 (o terminal e suas producoes)
        if len(p) != 2:
            raise ExcecaoAdicionarProducao("Deve haver apenas um simbolo " + SIMBOLO_SEPARADOR_PRODUCAO + " em toda a producao.")
        #se alfa for maior que um ou nao for maiuscula
        if len(p[0]) != 1 or str(p[0]) not in maiusculas:
            raise ExcecaoAdicionarProducao("Producao invalida. Alfa ("+str(p[0])+") deveria ser maiuscula e com apenas um caracter.")
        if str(p[0]) in self._infoGramaticaAtual["NaoTerminais"]:
            raise ExcecaoAdicionarProducao("Esse nao terminal ja foi utlizado, escolha outro")
        
        transicoes = p[1].split(SIMBOLO_SEPARADOR_TRANSICAO)
        
        #para cada uma das transicoes encontradas
        for t in transicoes:
            
            #transicoes no formato aA
            if len(t) == 2:
                #verifica se a primeira eh minuscula e a segunda maiuscula
                if str(t[0]) != str(t[0]).lower() or str(t[1]) != str(t[1]).upper():
                    raise ExcecaoAdicionarProducao("Transicao " + str(t) + " no formato errado. Deveria ser " + str(t[0]).lower() + str(t[1]).upper())
                elif str(t[1]) in numeros:
                    raise ExcecaoAdicionarProducao("Transicao invalida. O segundo simbolo nao pode ser um numero, deve ser uma letra maiuscula.")
                elif str(t[0]) not in numeros and str(t[0]) not in minusculas:
                    raise ExcecaoAdicionarProducao("Simbolo invalido na producao " + str(t) + ". Deve-se usar apenas letras ou numeros.")
                
            #transicoes no formato a
            elif len(t) == 1:
                #caso a primeira letra nao seja um terminal
                if str(t[0]) != str(t[0]).lower():
                    raise ExcecaoAdicionarProducao("A transicao " + str(t) + " esta no formato errado. Deveria ser " + str(t).lower())
                elif str(t[0]) not in numeros and str(t[0]) not in minusculas:
                    raise ExcecaoAdicionarProducao("Simbolo " + str(t[0]) + " eh invalido. Deve ser uma letra ou numero.")
                
            #caso nao atenda a nenhum dos formatos das gramaticas regulares
            else:
                #caso tenha mais de dois simbolos, nao pertence a GR
                raise ExcecaoAdicionarProducao("A transicao " + str(t) + " esta no formato errado. Deveria ter no maximo dois simbolos.")
        
        nt = self._infoGramaticaAtual["NaoTerminais"]
        self._infoGramaticaAtual["NaoTerminais"] = nt.union(str(p[0]))
        return True
    
    def _limparListaSentencas(self):
        """
        Limpa a lista de sentencas de tamanho n geradas pela gramatica
        """
        for _ in range(self.listaSentencas.count()): self.listaSentencas.takeItem(0)
    
    def _limparCaixasGramatica(self):
        """
        Limpa a caixa onde o usuario entra com a
        producao que deseja adicionar, e tambem limpa a caixa
        que contem o tamanho das sentencas que ele deseja gerar
        """
        self.caixaProducoes.setText("")
        self.caixaTamanhoProducoes.setText("")
        
    def _limparCaixasAutomato(self):
        """
        Limpa as caixas do automato: a caixa que o usuario usa para entrar
        com o novo simbolo do alfabeto, para entar com o novo estado que deseja
        adicionar e a caixa onde ele especifica uma sentenca que ele gostaria de saber
        se o automato reconhece ou nao
        """
        self.caixaAlfabeto.setText("")
        self.caixaEstado.setText("")
        self.caixaSentenca.setText("")
        
    def _limparEstados(self):
        """
        Limpa a lista de estados do automato
        """
        for _ in range(self.listaEstados.count()): self.listaEstados.removeItem(0)
        
    def _limparAlfabeto(self):
        """
        Limpa a lista de simbolos do alfabeto do automato
        """
        for _ in range(self.listaAlfabeto.count()): self.listaAlfabeto.removeItem(0)
        
    def _montarGramatica(self):
        """
        Monta a gramatica especificada na lista de producoes e lanca uma excecao
        caso alguma coisa nao esteja corretamente especificada
        Caso de tudo certo, retorna uma Gramatica
        """
        
        terminais = set([])
        nterminais = set([])
        producoes = []
        nterminaisFaltantes = set([])
        
        #para cada uma das producoes na lista de producoes:
        for indice in range(self.listaProducoes.count()):
            item = self.listaProducoes.item(indice).text()
            
            #cria uma nova producao e adiciona na lista de producoes
            p = item.split(SIMBOLO_SEPARADOR_PRODUCAO)
            producao = Producao(str(p[0]),str(p[1])) 
            producoes.append(producao)
            
            #adiciona o alfa na lista de nao terminais ja encontrados 
            nterminais.add(str(p[0]))
            nterminaisFaltantes.add(str(p[0])) #desnecessario?
            
            #agora separa as partes do beta e faz a mesma coisa
            for t in str(p[1]).split(SIMBOLO_SEPARADOR_TRANSICAO):
                if len(str(t)) == 2:
                    terminais.add(str(t[0]))
                    nterminaisFaltantes.add(str(t[1]))
                if len(str(t)) == 1 and str(t) != "&":
                    terminais.add(str(t))
                    
        #depois de montar todas as producoes, verifica se algum simbolo apareceu mas nao possui producao propria
        if nterminaisFaltantes.difference(nterminais) != set([]):
            raise ExcecaoImpossivelMontarGramatica("Gramatica invalida. Alguns nao terminais nao foram especificados: " + str(nterminaisFaltantes.difference(nterminais)) )
        if len(producoes) > 0:
            return Gramatica(producoes[0], nterminais, terminais, producoes)
        else:
            raise ExcecaoImpossivelMontarGramatica("Gramatica vazia")
                
    def _montarAutomato(self):
        """
        Monta o automato especificado na tabela de transicao
        e lanca uma excecao caso ele nao esteja corretamente
        especificado.
        Caso de tudo certo, retorna um Automato
        """
        tabelaTransicao = {}
        
        #verifica se o automato possui estado inicial e estados finais
        if self._infoAutomatoAtual["EstadoInicial"] == None:
            raise ExcecaoImpossivelMontarAutomato("O automato nao possui estado inicial.")
        if self._infoAutomatoAtual["EstadosFinais"] == set([]):
            raise ExcecaoImpossivelMontarAutomato(self,"Erro","O automato nao possui estados finais.")
        
        #para cada uma das linhas da tabela de transicoes
        for linha in range(self.tabelaTransicoes.rowCount()):
            aux = {}
            
            #para cada uma das colunas da tabela de transicoes
            for coluna in range(self.tabelaTransicoes.columnCount()):
                
                #pega o simbolo do alfabeto que vai para determinado estado
                simboloAlfabeto = str(self.tabelaTransicoes.horizontalHeaderItem(coluna).text())
                transicao = self.tabelaTransicoes.item(linha,coluna)
                
                #se nao for uma transicao vazia:
                if transicao != None and transicao.text() != "" :
                    transicao = str(transicao.text())

                    #verifica se o estado foi especificado ou se ele nao esta corretamente formado (por exemplo (AB, ou A,)
                    if (len(transicao) == 1 and transicao not in self._infoAutomatoAtual["Estados"] ) or len(transicao) % 2 == 0:
                        raise ExcecaoImpossivelMontarAutomato("A transicao " + transicao + " nao esta corretamente especificada na tabela.")

                    elif len(transicao) % 2 != 0:
                        for i in transicao:
                            if i != ",":
                                if i not in self._infoAutomatoAtual["Estados"]:
                                    raise ExcecaoImpossivelMontarAutomato("A transicao " + transicao + " nao esta corretamente especificada na tabela.")
                    aux[ simboloAlfabeto ] = transicao
#                else:
#                    transicao = ""
#                aux[ simboloAlfabeto ] = transicao
            estado = str(self.tabelaTransicoes.verticalHeaderItem(linha).text())
            estado = estado.replace("*","")
            estado = estado.replace("->","")
            tabelaTransicao[ estado ] = aux
            
        return Automato(tabelaTransicao, self._infoAutomatoAtual["Alfabeto"], self._infoAutomatoAtual["Estados"], 
                            self._infoAutomatoAtual["EstadoInicial"], self._infoAutomatoAtual["EstadosFinais"])
        
    def _limparProducoes(self):
        """
        Limpa a lista  que mostra todas as producoes da gramatica
        """
        for _ in range(self.listaProducoes.count()): self.listaProducoes.takeItem(0)
    
    def _mostrarGramatica(self, gramatica):
        """
        Limpa a lista de producoes, atualiza os dados da gramatica
        com a gramatica passada como parametro e mostra seus dados
        na lista de producoes
        """
        self._limparProducoes()
        self._atualizarGramatica(gramatica)
        
        #insere todos os outros itens
        for producao in gramatica.producoes:
            if producao != gramatica.producaoInicial:
                self.listaProducoes.insertItem(0,QListWidgetItem(str(producao)) )
                
        #insere a producao inicial
        self.listaProducoes.insertItem(0, QListWidgetItem(str(gramatica.producaoInicial)) )
        
    def _converterAFparaGR(self, automato):
        """
        Converte o automato finito passado para uma gramatica regular
        Assume-se que o automato passado esta corretamente especificado
        Retorna uma Gramatica
        """
        producoes = []
        
        #para cada um dos estados
        for estado in automato.tabelaTransicao.keys():
            transicoes = ""
            
            #para cada uma das transicoes desse estado
            transicao = automato.tabelaTransicao.get(estado)
            for trans in transicao.keys():

                #caso o caminho de destino seja final, coloca apenas o nao terminal
                if transicao.get(trans) in automato.estadosFinais:
                    transicoes += trans + "|"
                    
                t = automato.tabelaTransicao.get(transicao.get(trans))
                
                #caso o estado de destino tenha alguma transicao, coloca um caminho pra esse estado
                if len(t.keys()) > 0:
                    transicoes += trans + transicao.get(trans) + "|"
            
            #caso seja a producao inicial e seja final, coloca o epsilon
            if estado == automato.estadoInicial and estado in automato.estadosFinais:
                transicoes += "&" + "|"
                    
            #se nao for vazia, adiciona na lista de producoes
            if transicoes[:-1] != "":
                producoes.append(Producao(estado,transicoes[:-1]))
            
        for i in range(len(producoes)):
            producao = producoes[i]
            if producao.obterAlfa() == automato.estadoInicial:
                producaoInicial = producao
                break
            
        estados = ([p.obterAlfa() for p in producoes ])
        return Gramatica(producaoInicial,estados,automato.alfabeto,producoes)
    
    def _converterGRparaAF(self,gramatica):
        """
        Converte a gramatica regular passada para automato finito
        Assume-se que a gramatica passada esta corretamente especificada
        Retorna um Automato
        """
        estadosFinais = []
        if "F" not in gramatica.naoTerminais:
            estadoFinal = "F"
        else:
            possiveisNaoTerminais = map(chr, range(65, 91))
            for nt in possiveisNaoTerminais:
                if nt not in gramatica.naoTerminais:
                    estadoFinal = nt
                    break
                
        tabelaTransicao = {}
        
        for beta in gramatica.producaoInicial.obterListaBetas():
            if beta == "&":
                estadosFinais.append(gramatica.producaoInicial.obterAlfa())
        
        #para cada uma das producoes
        for producao in gramatica.producoes:
            
            novaTransicao = {}
            
            #para cada um dos betas dessa producao
            for beta in producao.obterListaBetas():
                
                #caso beta seja apenas um terminal
                if len(beta) == 1 and beta != "&":
                   
                    if novaTransicao.has_key(beta):
                        novaTransicao[beta] = novaTransicao[beta] + "," + estadoFinal
                    else:
                        novaTransicao[beta] = estadoFinal
              
                elif len(beta) == 2:
                    if novaTransicao.has_key(beta[0]):
                        novaTransicao[beta[0]] = beta[1] +","+ novaTransicao[beta[0]]
                    else:
                        novaTransicao[beta[0]] = beta[1]

                alfa = producao.obterAlfa()
                tabelaTransicao[alfa] = novaTransicao
        
        tabelaTransicao[estadoFinal] = {}
        estadosFinais.append(estadoFinal)
        return Automato( tabelaTransicao, gramatica.terminais, tabelaTransicao.keys(), gramatica.producaoInicial.obterAlfa(), estadosFinais)
        
#----------------------- classes de Excecao -----------------------        

class ExcecaoAdicionarProducao(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr("Producao invalida. " + self.value)
    
class ExcecaoImpossivelMontarAutomato(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr("Impossivel montar o automato. " + self.value)
        
class ExcecaoImpossivelMontarGramatica(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr("Impossivel montar a gramatica. " + self.value)
