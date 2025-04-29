from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QFont
import sys
import os

class JanelaPrincipal(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirigIA")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        DirigIA_White_path = os.path.join(base_dir, "recursos", "DirigIA_White.ico")
        self.setWindowIcon(QtGui.QIcon(DirigIA_White_path))   # Ícone da janela
        self.initUI()
        self.jbt_esconderMf = None
        self.menu_flutuante = None
        self.last_active_button_path = None  # Variável para registrar o último botão clicado
        self.last_active_background_path = None  # Variável para salvar o plano de fundo correspondente
        self.last_dirigia_state = None  # Para salvar o estado do botão BtSwtDMf
        self.installEventFilter(self)

    def initUI(self):
        self.showFullScreen()
        base_dir = os.path.dirname(os.path.abspath(__file__))   # Caminho base do projeto

        # Configuração do GIF de fundo
        Background_Carro_Animado_path = os.path.join(base_dir, "recursos", "Background_Carro_Animado.gif")
        self.bg_animation = QtGui.QMovie(Background_Carro_Animado_path)
        self.bg_label = QtWidgets.QLabel(self)  # Definindo bg_label como atributo da classe
        self.bg_label.setGeometry(self.rect())  # Ajusta o QLabel ao tamanho da janela
        self.bg_animation.setScaledSize(self.size())  # Faz o GIF ocupar toda a tela
        self.bg_label.setMovie(self.bg_animation)
        self.bg_animation.start()  # Inicia a animação do GIF
        
        # Garante que o GIF fique no fundo
        self.bg_label.lower()
    
        # Estado inicial do interruptor
        self.last_dirigia_state = "Desligado"
        self.bg_label.show()
        self.bg_animation.stop()
        print("BtSwtDMf está desligado. O GIF será congelado.") 

        # Configuração dos botões
        layout = QtWidgets.QVBoxLayout()
        self.BtIconAbrirMenu = QtWidgets.QPushButton(self)
        BtIconAbrirMenu_path = os.path.join(base_dir, "recursos", "BtIconAbrirMenu.png")
        BtIconAbrirMenu = QtGui.QIcon(BtIconAbrirMenu_path)
        self.BtIconAbrirMenu.setIcon(BtIconAbrirMenu)
        self.BtIconAbrirMenu.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
        self.BtIconAbrirMenu.setIconSize(QtCore.QSize(50, 50))
        self.BtIconAbrirMenu.setFixedSize(50, 50)
        self.BtIconAbrirMenu.clicked.connect(self.openMenuFlutuante)
        layout.addWidget(self.BtIconAbrirMenu)

        self.shutdownButton = QtWidgets.QPushButton(self)
        BtIconDesligarApp_path = os.path.join(base_dir, "recursos", "BtIconDesligarApp.png")
        BtIconDesligarApp = QtGui.QIcon(BtIconDesligarApp_path)
        self.shutdownButton.setIcon(BtIconDesligarApp)
        self.shutdownButton.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
        self.shutdownButton.setIconSize(QtCore.QSize(50, 50))
        self.shutdownButton.setFixedSize(50, 50)
        self.shutdownButton.clicked.connect(self.shutdownApplication)
        layout.addWidget(self.shutdownButton)

        centralWidget = QtWidgets.QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_label'):  # Verifica se bg_label foi inicializado
            self.bg_label.setGeometry(self.rect())  # Ajusta o QLabel ao tamanho da janela

    def saveLastState(self, button_path=None, background_path=None, dirigia_state=None):
        """
        Salva o botão ativo no QFrame ou o estado do botão BtSwtDMf.
        """
        if button_path and background_path:
            self.last_active_button_path = button_path
            self.last_active_background_path = background_path
            print(f"Estado salvo: Botão - {self.last_active_button_path}, Plano de Fundo - {self.last_active_background_path}")

        if dirigia_state is not None:
            self.last_dirigia_state = dirigia_state
            print(f"Estado salvo: BtSwtDMf - {self.last_dirigia_state}")

    def openMenuFlutuante(self):
        # Verifica se o menu já está aberto
        if hasattr(self, 'menu_flutuante') and self.menu_flutuante and self.menu_flutuante.isVisible():
            return  # Não faz nada se o menu já estiver aberto
        # Cria uma nova instância do MenuFlutuante
        self.menu_flutuante = MenuFlutuante(self)
        self.menu_flutuante.is_frozen = False  # Definir estado como ativado
        # Atualizar o visual do botão
        self.menu_flutuante.toggleFreeze()
        self.menu_flutuante.show()
        # Esconde o botão "Abrir Menu Flutuante"
        self.BtIconAbrirMenu.setVisible(False)
        # Conecta a destruição para reativar o botão
        self.menu_flutuante.destroyed.connect(self.onMenuDestroyed)
        # Passa o último estado salvo para o MenuFlutuante
                # Restaura os estados apenas se BtSwtDMf estiver ligado
        if self.last_dirigia_state == "Ligado":
            self.menu_flutuante.restoreLastState(
                self.last_active_button_path, self.last_active_background_path
            )
        if self.last_active_button_path and self.last_active_background_path:
            print(f"Restaurando último estado: Botão - {self.last_active_button_path}, Plano de Fundo - {self.last_active_background_path}")
            self.menu_flutuante.restoreLastState(self.last_active_button_path, self.last_active_background_path)
        else:
            print("Erro: Estado anterior não encontrado.")
        self.menu_flutuante.show()

    def focusOutEvent(self, event):
        if self.is_frozen:  # Esconde apenas se o interruptor estiver ativado
            self.hide()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if self.menu_flutuante and self.menu_flutuante.isVisible():
                if self.menu_flutuante.is_frozen and not self.menu_flutuante.geometry().contains(event.globalPos()):
                    self.menu_flutuante.hide()  # Esconde o menu apenas se o interruptor estiver ativado
                    self.menu_flutuante.hide()  # Esconde o menu
                    self.BtIconAbrirMenu.setVisible(True)  # Reaparece o botão aqui
        return super().eventFilter(obj, event)

    def onMenuDestroyed(self):
        # Mostra novamente o botão
        self.BtIconAbrirMenu.setVisible(True)

    def shutdownApplication(self):
        QtWidgets.QApplication.quit()

class MenuFlutuante(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Referência à JanelaPrincipal
        self.last_background = None  # Inicializa a variável para evitar erros
        self.last_active_button = None  # Variável para o botão ativo
        self.initUI()
        self.menu_flutuante_config = None  # Inicializa como None
        self.jbt_esconder = None  # Inicializa como None
        self.is_frozen = True  # Variável para controlar o estado de congelamento
        self.offset = None  # Armazena a posição inicial do clique/touch
        self.bg_label = None
        self.bg_animation = None
        
    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)     
        base_dir = os.path.dirname(os.path.abspath(__file__))   # Caminho base do projeto

        # Carregar a imagem de fundo
        Menu_flutuante_path = os.path.join(base_dir, "recursos", "Menu_flutuante.png")
        self.bg_image = QtGui.QPixmap(Menu_flutuante_path)

        # Definir tamanho e proporção da janela
        self.original_width = self.bg_image.width()
        self.original_height = self.bg_image.height()
        self.nova_largura = int(self.original_width * 0.8)
        self.nova_altura = int(self.original_height * 0.8)
        self.setGeometry(100, 100, self.nova_largura, self.nova_altura)

        # Botão DirigIA
        self.BtSwtDMf = QtWidgets.QPushButton("", self)
        self.BtSwtDMf.setGeometry(int(270 * 0.8), int(40 * 0.8), int(100 * 0.8), int(100 * 0.8))

        # Inicia com o estado "Desligado"
        self.BtSwtDMf.state = False  # False = Desligado, True = Ligado
        BtSwtDMfDlgd_path = os.path.join(base_dir, "recursos", "BtSwtDMfDlgd.png")
        BtSwtDMfDlgd = QtGui.QIcon(BtSwtDMfDlgd_path)
        self.BtSwtDMf.setIcon(BtSwtDMfDlgd)
        self.BtSwtDMf.setStyleSheet("""QPushButton {background-color: rgba(0, 0, 0, 0); text-align: right;}""")
        self.BtSwtDMf.setIconSize(QtCore.QSize(100, 100))
        self.BtSwtDMf.clicked.connect(self.confirmStateChange)

        # Botão para esconder a janela
        self.buttonesconder = QtWidgets.QPushButton("", self)
        self.buttonesconder.setGeometry(int(319 * 0.8), int(13 * 0.8), int(50 * 0.8), int(50 * 0.8))
        IconEsconderConfigDesativado_path = os.path.join(base_dir, "recursos", "IconEsconderConfigDesativado.png")
        IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
        self.buttonesconder.setIcon(IconesconderConfigDesativado)
        self.buttonesconder.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
        self.buttonesconder.setIconSize(QtCore.QSize(50, 50))
        self.buttonesconder.clicked.connect(self.toggleFreeze)

                # Ajustar a proporção do botão
        self.button = QtWidgets.QPushButton("", self)
        self.button.setGeometry(int(40 * 0.8), int(433 * 0.8), int(290 * 0.8), int(70 * 0.8))  # Proporcionalmente ajustado
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        # Conectar eventos de toque e clique ao botão
        self.button.clicked.connect(self.openNewFloatingWindow)

        # Criação do QFrame dentro da classe
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(6, 624, 380, 160)  # Ajuste a posição e tamanho
        self.frame.setStyleSheet("border-radius: 10px;")  # Remove cor de fundo padrão

        # Botões e seus nomes associados
        self.BtPfCritiMf = QtWidgets.QPushButton("", self.frame)
        self.BtPfRecoMf = QtWidgets.QPushButton("", self.frame)
        self.BtPfEssenMf = QtWidgets.QPushButton("", self.frame)
        self.BtPfCritiMf.setObjectName("Crítico")
        self.BtPfRecoMf.setObjectName("Recomendado")
        self.BtPfEssenMf.setObjectName("Essencial")

        # Imagens associadas aos botões
        self.icons = {
            "Crítico": os.path.join(base_dir, "recursos", "BtPfCritiMf.png"),
            "Recomendado": os.path.join(base_dir, "recursos", "BtPfRecoMf.png"),
            "Essencial": os.path.join(base_dir, "recursos", "BtPfEssenMf.png"),
        }
        # Configuração inicial dos botões
        self.BtPfCritiMf.setGeometry(250, 0, 128, 160)
        self.BtPfCritiMf.setStyleSheet(self.buttonStyle())
        self.BtPfCritiMf.clicked.connect(lambda: self.handleCustomClick(self.BtPfCritiMf))

        self.BtPfRecoMf.setGeometry(126, 0, 128, 160)
        self.BtPfRecoMf.setStyleSheet(self.buttonStyle())
        self.BtPfRecoMf.clicked.connect(lambda: self.handleCustomClick(self.BtPfRecoMf))

        self.BtPfEssenMf.setGeometry(2, 0, 128, 160)
        self.BtPfEssenMf.setStyleSheet(self.buttonStyle())
        self.BtPfEssenMf.clicked.connect(lambda: self.handleCustomClick(self.BtPfEssenMf))

    def handleCustomClick(self, button):
        """
        Lida com cliques nos botões BtPfCritiMf, BtPfRecoMf e BtPfEssenMf com base no estado do BtSwtDMf.
        """
        if not self.BtSwtDMf.state:  # BtSwtDMf está Desligado
            print(f"BtSwtDMf está Desligado. Ativando e destacando o botão correspondente: {button.objectName()}.")

        # Exibe o perfil_frame (contagem regressiva)
            self.showPerfilFrame(button)

            # Destaca o botão clicado
            self.highlightButton(button.objectName())

            # Simula cliques reais no botão clicado
            print("Chamando simulateClicks...")
            self.simulateClicks(button)
        else:    # BtSwtDMf está Ativado
            print(f"BtSwtDMf está Ativado. Executando a ação diretamente para {button.objectName()}.")
            self.changeBackground(button.objectName())  # Segue diretamente para alterar o fundo

    def buttonStyle(self):
        """
        Retorna o estilo dos botões com transparência e bordas destacadas.
        """
        return (
            "background-color: rgba(0, 0, 0, 0);"
            "border-radius: 10px;"
        )
    def changeBackground(self, button_name):
        """
        Alterar o plano de fundo do QFrame conforme o botão selecionado.
        """
        image_path = self.icons.get(button_name)  # Busca o caminho da imagem pelo nome do botão
        print(f"Alterando plano de fundo para: {image_path}")

        if not image_path or not QtCore.QFile.exists(image_path):  # Verifica se o caminho é válido
            print(f"Erro: Caminho inválido ou inexistente - {image_path}")
            return
        self.last_background = image_path
        self.last_active_button = button_name

        self.parent_window.saveLastState(button_name, image_path)
        # Aplicar o plano de fundo no QFrame
        self.applyBackground(image_path)
        self.highlightButton(button_name)
    
    def highlightButton(self, button_name):
        """
        Destaca o botão clicado e redefine o estilo dos demais.
        """
        for name, button in [("BtPfCritiMf", self.BtPfCritiMf), 
                             ("BtPfRecoMf", self.BtPfRecoMf), 
                             ("BtPfEssenMf", self.BtPfEssenMf)]:
            if name == button_name:
                button.setStyleSheet(
                    "background-color: rgba(0, 0, 0, 0);"
                )
            else:
                button.setStyleSheet(self.buttonStyle())  # Redefine o estilo padrão
    
    def applyBackground(self, image_path):
        """
        Aplica o plano de fundo ao QFrame.
        """
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            print(f"Erro: O QPixmap não conseguiu carregar a imagem - {image_path}")
            return

        print(f"Aplicando plano de fundo: {image_path}")
        scaled_pixmap = pixmap.scaled(
            self.frame.size(),
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )
        palette = self.frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(scaled_pixmap))
        self.frame.setPalette(palette)
        self.frame.setAutoFillBackground(True)
        self.frame.update()
        self.frame.repaint()

    def restoreLastState(self, button_name=None, background_path=None):
        """
        Restaura o último botão ativo e aplica seu plano de fundo (do QFrame).
        Também restaura o estado do botão BtSwtDMf.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        last_state = self.parent_window.last_dirigia_state
        if last_state == "Ligado":
            BtSwtDMfLgd_path = os.path.join(base_dir, "recursos", "BtSwtDMfLgd.png")
            BtSwtDMfLgd = QtGui.QIcon(BtSwtDMfLgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfLgd)
            self.BtSwtDMf.state = True
            print("BtSwtDMf restaurado para: Ligado")
        else:
            BtSwtDMfDlgd_path = os.path.join(base_dir, "recursos", "BtSwtDMfDlgd.png")
            BtSwtDMfDlgd = QtGui.QIcon(BtSwtDMfDlgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfDlgd)
            self.BtSwtDMf.state = False
            print("BtSwtDMf restaurado para: Desligado")
            return

        # Restaurar o último botão ativo do QFrame
        if button_name and background_path:
            print(f"Restaurando botão: {button_name}, Plano de fundo: {background_path}")
            self.applyBackground(background_path)
            self.highlightButton(button_name)

            if not background_path or not QtCore.QFile.exists(background_path):
                print(f"Erro: Caminho da imagem inválido ou inexistente - {background_path}")
                return

            # Aplicar plano de fundo e destacar o botão
            self.applyBackground(background_path)
            self.highlightButton(button_name)

    def show(self):
        """
        Mostra a janela.
        """
        super().show()

    def toggleFreeze(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))   # Caminho base do projeto
        self.is_frozen = not self.is_frozen
        if self.is_frozen:
            IconEsconderConfigAtivado_path = os.path.join(base_dir, "recursos", "IconEsconderConfigAtivado.png")
            IconesconderConfigAtivado = QtGui.QIcon(IconEsconderConfigAtivado_path)
            self.buttonesconder.setIcon(IconesconderConfigAtivado)
            self.buttonesconder.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
            self.buttonesconder.setIconSize(QtCore.QSize(50, 50))
        else:
            IconEsconderConfigDesativado_path = os.path.join(base_dir, "recursos", "IconEsconderConfigDesativado.png")
            IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
            self.buttonesconder.setIcon(IconesconderConfigDesativado)
            self.buttonesconder.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
            self.buttonesconder.setIconSize(QtCore.QSize(50, 50))

    def confirmStateChange(self):
        """
        Mostra um alerta com 80% de transparência antes de mudar o estado do botão BtSwtDMf.
        Agora, os elementos visíveis (contador e botão cancelar) estão dentro de um QFrame.
        """
        self.BtSwtDMf.setEnabled(False)
        self.alert_dialog = QtWidgets.QDialog(self)

        # Definir a janela como transparente, mantendo os elementos visíveis dentro do QFrame
        self.alert_dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.alert_dialog.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.alert_dialog.setStyleSheet("background-color: transparent; border: none;")

        # Criando um QFrame dentro do QDialog para isolar os elementos visíveis
        self.local_frame = QtWidgets.QFrame(self)
        self.local_frame.setGeometry(231, 323, 170, 130)  # Ajuste de posição e tamanho
        self.local_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0); border-radius: 15px;")  # Apenas o QFrame será visível

        # Criando um layout para organizar os elementos dentro do QFrame
        layout = QtWidgets.QVBoxLayout(self.local_frame)

        # Configuração do contador regressivo
        self.countdown_label = QtWidgets.QLabel("5", self.local_frame)
        self.countdown_label.setAlignment(QtCore.Qt.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 36px; font-weight: bold; color: black;")

        # Configuração do botão cancelar
        self.cancel_button_BtSwt = QtWidgets.QPushButton("CANCELAR", self.local_frame)
        self.cancel_button_BtSwt.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background-color: rgba(0, 143, 122, 100);
                color: black;
                border-radius: 10px;
                border: 1px solid #008e9b;
            }
        """)
        # Criar a QLabel para o texto do botão
        self.text_cancel_BtSwt = QtWidgets.QLabel("CANCELAR", self.cancel_button_BtSwt)
        self.text_cancel_BtSwt.setAlignment(QtCore.Qt.AlignCenter)  # Centraliza o texto
        self.text_cancel_BtSwt.setFont(QFont("Arial", 12, QFont.Bold))
        self.text_cancel_BtSwt.setStyleSheet("color: black;")
        self.text_cancel_BtSwt.setGeometry(13, 2, 120, 50)  # Ajustar ao tamanho e geometria do botão
        # Aplicar o efeito de contorno ao texto
        shadow_effect_CancelBtSwt = QGraphicsDropShadowEffect()
        shadow_effect_CancelBtSwt.setColor(QColor("white"))  # Cor do contorno
        shadow_effect_CancelBtSwt.setOffset(0, 0)             # Sem deslocamento
        shadow_effect_CancelBtSwt.setBlurRadius(10)           # Raio do desfoque
        self.text_cancel_BtSwt.setGraphicsEffect(shadow_effect_CancelBtSwt)
        self.cancel_button_BtSwt.clicked.connect(self.cancelStateChange)

        # Adicionando os elementos ao layout do QFrame
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.cancel_button_BtSwt)
        self.local_frame.setLayout(layout)  # Aplicando layout ao QFrame

        # Criando o temporizador para contagem regressiva
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)  # Intervalo de 1 segundo
        self.remaining_time = 5  # Define a contagem regressiva inicial
        self.timer.timeout.connect(self.updateCountdown)

        # Exibir o QDialog e o QFrame corretamente
        self.alert_dialog.show()
        self.local_frame.show()
        QtWidgets.QApplication.processEvents()
        self.timer.start()

    def updateCountdown(self):
        """
        Atualiza a contagem regressiva dentro do alerta.
        """
        if self.remaining_time > 1:
            self.remaining_time -= 1
            self.countdown_label.setText(str(self.remaining_time))
        else:
            self.timer.stop()
            if self.local_frame.isVisible():  # Verifica se o QFrame está visível
                self.local_frame.close()
                self.alert_dialog.close()
                self.BtSwtDMf.setEnabled(True)
            self.toggleDirigIA()  # Alternar estado após a contagem regressiva

    def cancelStateChange(self):
        """
        Cancela a alteração do estado do botão BtSwtDMf e fecha o QFrame.
        """
        self.timer.stop()
        if self.local_frame.isVisible():  # Verifica se o QFrame está visível
            self.local_frame.close()
            self.alert_dialog.close()
            self.BtSwtDMf.setEnabled(True)
        print("Alteração cancelada pelo usuário.")

    def toggleDirigIA(self):
        """
        Alterna o estado do botão BtSwtDMf entre "Desligado" e "Ligado".
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not self.BtSwtDMf.state:  # Estado atual é Desligado
            # Mudança para "Ligado"
            BtSwtDMfLgd_path = os.path.join(base_dir, "recursos", "BtSwtDMfLgd.png")
            BtSwtDMfLgd = QtGui.QIcon(BtSwtDMfLgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfLgd)
            self.BtSwtDMf.state = True  # Atualiza o estado para Ligado
            self.parent_window.saveLastState(None, None, "Ligado")
            print("BtSwtDMf: DirigIA Ligado")
    
            # Agora acessamos o GIF de fundo corretamente
            if hasattr(self.parent_window, "bg_label") and hasattr(self.parent_window, "bg_animation"):
                self.parent_window.bg_label.show()
                self.parent_window.bg_animation.start()
                print("BtSwtDMf está ligado. O GIF será exibido.")
            else:
                print("Erro: bg_label ou bg_animation não encontrados na JanelaPrincipal.")
    
            # Simula dois cliques reais no botão BtPfRecoMf
            print("Chamando simulateClicks...")
            self.simulateClicks(self.BtPfRecoMf)
    
        else:
            # Mudança para "Desligado"
            BtSwtDMfDlgd_path = os.path.join(base_dir, "recursos", "BtSwtDMfDlgd.png")
            BtSwtDMfDlgd = QtGui.QIcon(BtSwtDMfDlgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfDlgd)
            self.BtSwtDMf.state = False  # Atualiza o estado para Desligado
            self.parent_window.saveLastState(None, None, "Desligado")
            print("BtSwtDMf: DirigIA Desligado")
    
            # Atualiza o estado global
            self.parent_window.last_dirigia_state = "Ligado" if self.BtSwtDMf.state else "Desligado"
            print(f"Estado salvo: BtSwtDMf - {'Ligado' if self.BtSwtDMf.state else 'Desligado'}")
    
            # Restaura o estado inicial dos botões do QFrame
            self.resetQFrameButtons()
    
            # Agora acessamos o GIF de fundo corretamente
            if hasattr(self.parent_window, "bg_label") and hasattr(self.parent_window, "bg_animation"):
                self.parent_window.bg_animation.stop()
                print("BtSwtDMf está desligado. O GIF será congelado.")
            else:
                print("Erro: bg_label ou bg_animation não encontrados na JanelaPrincipal.")
    
    def showPerfilFrame(self, button):
        """
        Exibe um QDialog chamado perfil_frame com contagem regressiva e mensagem personalizada.
        """
        if self.BtSwtDMf.state:  # Botão está ativado
            print(f"BtSwtDMf está ativado. Continuando para o método changeBackground com o botão {button.objectName()}.")
            self.changeBackground(button.objectName())  # Executa o método changeBackground normalmente
            return

        #Desabilitar os botões
        self.BtPfCritiMf.setEnabled(False)
        self.BtPfRecoMf.setEnabled(False)
        self.BtPfEssenMf.setEnabled(False)
        self.BtSwtDMf.setEnabled(False)
        print("Botões desabilitados após o clique.")

        # Criando o QDialog
        self.perfil_frame = QtWidgets.QDialog(self)

        # Configuração do QDialog
        self.perfil_frame.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.perfil_frame.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.perfil_frame.setStyleSheet("background-color: transparent; border: none;")
        self.perfil_frame.setFixedSize(300, 200)

        #Criando um Qframe dentro do QDialog para isolar os elementos visíveis
        self.frame_perfil = QtWidgets.QFrame(self)
        self.frame_perfil.setGeometry(1,518,396,310)  # Ajuste de posição e tamanho
        self.frame_perfil.setStyleSheet("background-color: rgba(0, 0, 0, 0); border-radius: 15px;")  # Apenas o QFrame será visível

        # Configuração do layout interno
        layout = QtWidgets.QVBoxLayout(self.perfil_frame)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margens

        self.perfil_frame_label1 = QtWidgets.QLabel(f"                       {button.objectName()}                 \n               Ativando DirigIA ...     ")
        self.perfil_frame_label1.setStyleSheet("font-size: 27px; font-weight: bold; color: black;")
        self.perfil_frame_label1.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        #self.perfil_frame_label1.setFixedSize(300,200)
        # Mensagem personalizada
        self.perfil_frame_label2 = QtWidgets.QLabel(f"                       {button.objectName()}                 \n               Ativando DirigIA ...     ", self.perfil_frame_label1)
        self.perfil_frame_label2.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        self.perfil_frame_label2.setStyleSheet("font-size: 27px; font-weight: bold; color: #4ffbdf;")
        self.perfil_frame_label2.setGeometry(0, -5, 395, 100)
        shadow_effectTxPf = QGraphicsDropShadowEffect()
        shadow_effectTxPf.setColor(QColor("black"))   #Cor do contorno
        shadow_effectTxPf.setOffset(0, 0)   #Sem deslocamento
        shadow_effectTxPf.setBlurRadius(10) #Raio do desfoque para o contorno
        self.perfil_frame_label2.setGraphicsEffect(shadow_effectTxPf)
        self.perfil_frame_label2.show()

        # Contador regressivo
        self.perfil_countdown_label = QtWidgets.QLabel("5", self.perfil_frame)
        self.perfil_countdown_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        self.perfil_countdown_label.setStyleSheet("font-size: 36px; font-weight: bold; color: black;")
        shadow_effect_contador_perfil = QGraphicsDropShadowEffect()
        shadow_effect_contador_perfil.setColor(QColor("white"))  # Cor do contorno
        shadow_effect_contador_perfil.setOffset(0, 0)             # Sem deslocamento
        shadow_effect_contador_perfil.setBlurRadius(10)           # Raio do desfoque
        self.perfil_countdown_label.setGraphicsEffect(shadow_effect_contador_perfil)

        # Criar o botão CANCELAR
        self.cancel_perfil = QtWidgets.QPushButton("                            CANCELAR                            ", self.perfil_frame)
        self.cancel_perfil.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                padding: 16px;
                background-color: rgba(0, 143, 122, 100);
                color: black;
                border-radius: 10px;
                border: 1px solid #008e9b;
            }
        """)
        # Criar a QLabel para o texto do botão
        self.text_cancel_perfil = QtWidgets.QLabel("CANCELAR", self.cancel_perfil)
        self.text_cancel_perfil.setAlignment(QtCore.Qt.AlignCenter)  # Centraliza o texto
        self.text_cancel_perfil.setFont(QFont("Arial", 13, QFont.Bold))
        self.text_cancel_perfil.setStyleSheet("color: black;")
        self.text_cancel_perfil.setGeometry(135, 19, 125, 20)  # Ajustar ao tamanho e geometria do texto do botão
        
        # Aplicar o efeito de contorno ao texto
        shadow_effect_cancel_perfil = QGraphicsDropShadowEffect()
        shadow_effect_cancel_perfil.setColor(QColor("white"))  # Cor do contorno
        shadow_effect_cancel_perfil.setOffset(0, 0)             # Sem deslocamento
        shadow_effect_cancel_perfil.setBlurRadius(10)           # Raio do desfoque
        self.text_cancel_perfil.setGraphicsEffect(shadow_effect_cancel_perfil)
        self.cancel_perfil.clicked.connect(self.cancelStatePerfil)
        
        # Adicionando os elementos ao layout
        layout.addWidget(self.perfil_frame_label1)
        layout.addWidget(self.cancel_perfil, alignment=Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.perfil_countdown_label)
        self.frame_perfil.setLayout(layout) #Aplicando layout ao frame

        # Criando o temporizador para contagem regressiva
        self.perfil_timer = QtCore.QTimer(self)
        self.perfil_timer.setInterval(1000)  # Intervalo de 1 segundo
        self.perfil_remaining_time = 5  # Define a contagem inicial
        self.perfil_timer.timeout.connect(lambda: self.updatePerfilCountdown(button))  # Passa o botão clicado

        # Exibe o QDialog e inicia o temporizador
        self.perfil_frame.show()
        self.frame_perfil.show()
        QtWidgets.QApplication.processEvents()
        self.perfil_timer.start()

    def updatePerfilCountdown(self, button):
        """
        Atualiza a contagem regressiva do perfil_frame.
        Após o término:
        - Ativa automaticamente o botão BtSwtDMf chamando toggleDirigIA.
        - Seleciona e destaca o botão correspondente ao clique (BtPfCritiMf, BtPfRecoMf, BtPfEssenMf).
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if self.perfil_remaining_time > 1:
            self.perfil_remaining_time -= 1
            self.perfil_countdown_label.setText(str(self.perfil_remaining_time))
        else:
            self.perfil_timer.stop()
            if self.frame_perfil.isVisible():  #Verifica se o frame está visível
                self.frame_perfil.close()
                self.perfil_frame.close()
                print("perfil_frame fechado após a contagem regressiva.")

            # Mudança para "Ligado"
            BtSwtDMfLgd_path = os.path.join(base_dir, "recursos", "BtSwtDMfLgd.png")
            BtSwtDMfLgd = QtGui.QIcon(BtSwtDMfLgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfLgd)
            self.BtSwtDMf.state = True  # Atualiza o estado para Ligado
            self.parent_window.saveLastState(None, None, "Ligado")
            print("BtSwtDMf: DirigIA Ligado")

            # Agora acessamos o GIF de fundo corretamente
            if hasattr(self.parent_window, "bg_label") and hasattr(self.parent_window, "bg_animation"):
                self.parent_window.bg_label.show()
                self.parent_window.bg_animation.start()
                print("BtSwtDMf está ligado. O GIF será exibido.")
            else:
                print("Erro: bg_label ou bg_animation não encontrados na JanelaPrincipal.")
            
            # Destaca o botão clicado
            print(f"Destacando o botão correspondente: {button.objectName()}")
            self.highlightButton(button.objectName())
            # Reabilitar os botões
            self.BtPfCritiMf.setEnabled(True)
            self.BtPfRecoMf.setEnabled(True)
            self.BtPfEssenMf.setEnabled(True)
            self.BtSwtDMf.setEnabled(True)
            print("Botões reabilitados após a contagem regressiva.")
            #Simula os cliques no botão correspondente
            print(f"Chamando simulateClicksperfil para {button.objectName()}.")
            self.simulateClicksperfil(button)

    def cancelStatePerfil(self):
        self.perfil_timer.stop()
        if self.frame_perfil.isVisible():
            self.frame_perfil.close()
            self.perfil_frame.close()
            print("Alteração de perfil realizada pelo usuário!")
            # Reabilitar os botões
            self.BtPfCritiMf.setEnabled(True)
            self.BtPfRecoMf.setEnabled(True)
            self.BtPfEssenMf.setEnabled(True)
            self.BtSwtDMf.setEnabled(True)

    def resetQFrameButtons(self):
        """
        Restaura o estado inicial dos botões do QFrame (nenhum botão selecionado).
        """
        self.BtPfCritiMf.setStyleSheet(self.buttonStyle())
        self.BtPfRecoMf.setStyleSheet(self.buttonStyle())
        self.BtPfEssenMf.setStyleSheet(self.buttonStyle())

        # Remove o plano de fundo aplicado no QFrame
        self.frame.setAutoFillBackground(False)
        self.frame.update()
        print("Botões do QFrame restaurados ao estado inicial.")

    def simulateClicks(self, button, num_clicks=2):
        """
        Simula cliques reais no botão especificado do QFrame, garantindo que o evento ocorra corretamente.
        """
        if self.BtPfRecoMf is None or not self.BtPfRecoMf.isVisible():
            print("Erro: O botão BtPfRecoMf não está disponível para clique.")
            return

        print(f"Entrou em simulateClicks para o botão {button.objectName()}")
        """
        Simula cliques reais no botão especificado do QFrame.
        """
        for _ in range(num_clicks):
            print(f"Simulando clique em {button.rect().center()}")
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.MouseButtonPress,
                    button.rect().center(),
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.NoModifier
                )
            )
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.MouseButtonRelease,
                    button.rect().center(),
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.NoButton,
                    QtCore.Qt.NoModifier
                )
            )
        print(f"Simulação de clique real realizada no botão {button.objectName()}.")

    def simulateClicksperfil(self, button, num_clicks=2):
        """
        Simula cliques reais no botão especificado do QFrame.
        """
        if button is None or not button.isVisible():
            print(f"Erro: O botão {button.objectName() if button else 'None'} não está disponível para clique.")
            return
    
        print(f"Entrou em simulateClicks para o botão {button.objectName()}")
    
        # Simula cliques reais no botão
        for _ in range(num_clicks):
            print(f"Simulando clique em {button.rect().center()}")
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.MouseButtonPress,
                    button.rect().center(),
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.NoModifier
                )
            )
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.MouseButtonRelease,
                    button.rect().center(),
                    QtCore.Qt.LeftButton,
                    QtCore.Qt.NoButton,
                    QtCore.Qt.NoModifier
                )
            )
        print(f"Simulação de clique real realizada no botão {button.objectName()}.")
    
        # Chamar changeBackground após simulação
        self.changeBackground(button.objectName())

    def resizeEvent(self, event):
        new_size = event.size()
        width_ratio = new_size.width() / self.nova_largura
        height_ratio = new_size.height() / self.nova_altura
        self.nova_largura = int(self.original_width * width_ratio)
        self.nova_altura = int(self.original_height * height_ratio)
        self.setGeometry(self.geometry().x(), self.geometry().y(), self.nova_largura, self.nova_altura)
        self.BtSwtDMf.setGeometry(int(40 *width_ratio), int(320 *height_ratio), int(300 *width_ratio), int(77 *height_ratio))
        self.buttonesconder.setGeometry(int(333 * width_ratio), int(11 * height_ratio), int(50 * width_ratio), int(50 * height_ratio))
        self.button.setGeometry(int(40 * width_ratio), int(433 * height_ratio), int(290 * width_ratio), int(70 * height_ratio))
        super().resizeEvent(event)

    def paintEvent(self, event):
        """
        Método para desenhar o plano de fundo personalizado.
        """
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.bg_image.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def focusOutEvent(self, event):
        """
        Esconde a janela ao perder o foco, caso o interruptor esteja desligado.
        """
        if not self.is_frozen:
            self.hide()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        """
        Evento chamado ao pressionar o botão do mouse.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()  # Armazena a posição inicial do clique

    def mouseMoveEvent(self, event):
        """
        Evento chamado ao mover o mouse enquanto o botão esquerdo está pressionado.
        """
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            # Calcula a nova posição da janela
            delta = event.globalPos() - self.offset
            self.move(delta)

    def mouseReleaseEvent(self, event):
        """
        Evento chamado ao soltar o botão do mouse.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = None  # Reseta o deslocamento quando o clique for solto

    def touchEvent(self, event):
        """
        Captura eventos de toque no caso de dispositivos touch.
        """
        if event.type() == QtCore.QEvent.TouchBegin:
            self.offset = event.pos()
        elif event.type() == QtCore.QEvent.TouchUpdate and self.offset is not None:
            delta = event.globalPos() - self.offset
            self.move(delta)
        elif event.type() == QtCore.QEvent.TouchEnd:
            self.offset = None  # Reseta ao finalizar o toque

    def StartDirigIA(self):
        """
        Placeholder para iniciar funcionalidades relacionadas a DirigIA.
        """
        pass

    def PerfisMenuFlutuante(self):
        """
        Placeholder para gerenciar perfis do menu flutuante.
        """
        pass

    def openNewFloatingWindow(self):
        """
        Abre janelas flutuantes adicionais, como perfis e configurações.
        """
        if not self.jbt_esconder:  # Verifica se a janela "jbt_esconder" já foi criada
            self.jbt_esconder = JbtEsconder(self.parent())
            self.jbt_esconder.show()
        else:
            self.jbt_esconder.show()

        if not self.menu_flutuante_config:  # Verifica se a nova janela já foi criada
            self.menu_flutuante_config = MenuFlutuanteConfig(self.parent())
            self.menu_flutuante_config.is_frozen = False
            self.menu_flutuante_config.toggleFreeze()
            self.menu_flutuante_config.move(self.geometry().right() + 20, self.geometry().top())
            self.menu_flutuante_config.show()
        else:
            self.menu_flutuante_config.show()

    def focusOutEvent(self, event):
        """
        Esconde a janela ao perder o foco, caso o interruptor esteja desligado.
        """
        if not self.is_frozen:
            self.hide()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        """
        Filtra eventos específicos relacionados ao botão principal.
        """
        if obj == self.button and (event.type() == QtCore.QEvent.TouchBegin or event.type() == QtCore.QEvent.MouseButtonPress):
            return True
        return super().eventFilter(obj, event)

class JbtEsconder(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnBottomHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())

        self.bt_esconder = QtWidgets.QPushButton(self)
        self.bt_esconder.setGeometry(0, 0, self.width(), self.height())
        self.bt_esconder.setStyleSheet("background-color: rgba(255, 0, 0, 0.0); border: solid;")
        self.bt_esconder.clicked.connect(self.hideMenuFlutuanteConfig)

    def hideMenuFlutuanteConfig(self):
        if self.parent() and hasattr(self.parent(), 'menu_flutuante'):
            if self.parent().menu_flutuante.menu_flutuante_config:
                if self.parent().menu_flutuante.menu_flutuante_config.is_frozen:
                    self.parent().menu_flutuante.menu_flutuante_config.hide()
        self.hide()

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.bt_esconder.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

class MenuFlutuanteConfig(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.is_frozen = True  # Variável para controlar o estado de congelamento
        self.offset = None  # Variável para armazenar o deslocamento inicial

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        base_dir = os.path.dirname(os.path.abspath(__file__))   # Caminho base do projeto

        # Carregar a imagem de fundo
        Menu_flutuante_Config_path = os.path.join(base_dir, "recursos", "Menu_flutuante_Config.png")
        self.bg_image = QtGui.QPixmap(Menu_flutuante_Config_path)

        # Definir a proporção da janela para 80% da imagem original
        self.original_width = self.bg_image.width()
        self.original_height = self.bg_image.height()
        self.nova_largura = int(self.original_width * 0.8)
        self.nova_altura = int(self.original_height * 0.8)
        self.setGeometry(120, 100, self.nova_largura, self.nova_altura)  # Ajuste a posição inicial da nova janela

        # Ajustar a proporção do botão
        self.button = QtWidgets.QPushButton("", self)
        self.button.setGeometry(int(319 * 0.8), int(13 * 0.8), int(50 * 0.8), int(50 * 0.8))  # Proporcionalmente ajustado
        IconEsconderConfigDesativado_path = os.path.join(base_dir, "recursos", "IconEsconderConfigDesativado.png")
        IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
        self.button.setIcon(IconesconderConfigDesativado)
        self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
        self.button.setIconSize(QtCore.QSize(50, 50))
        # Conectar eventos de toque e clique ao botão
        self.button.clicked.connect(self.toggleFreeze)

    # Adicione os métodos de movimentação abaixo:
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()  # Armazena a posição inicial do clique

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            # Calcula a nova posição da janela
            delta = event.globalPos() - self.offset
            self.move(delta)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = None  # Reseta o deslocamento quando o clique for solto

    def touchEvent(self, event):
        # Captura eventos de toque no caso de dispositivos touch
        if event.type() == QtCore.QEvent.TouchBegin:
            self.offset = event.pos()
        elif event.type() == QtCore.QEvent.TouchUpdate and self.offset is not None:
            delta = event.globalPos() - self.offset
            self.move(delta)
        elif event.type() == QtCore.QEvent.TouchEnd:
            self.offset = None  # Reseta ao finalizar o toque

    def toggleFreeze(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.is_frozen = not self.is_frozen  # Alternar o estado
        if self.is_frozen:
            # Configuração para estado ativado
            IconEsconderConfigAtivado_path = os.path.join(base_dir, "recursos", "IconEsconderConfigAtivado.png")
            IconesconderConfigAtivado = QtGui.QIcon(IconEsconderConfigAtivado_path)
            self.button.setIcon(IconesconderConfigAtivado)
            self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
            self.button.setIconSize(QtCore.QSize(50, 50))
            if self.parent() and hasattr(self.parent(), 'menu_flutuante'):
                if self.parent().menu_flutuante.jbt_esconder:
                    self.parent().menu_flutuante.jbt_esconder.show()
        else:
            # Configuração para estado desativado
            IconEsconderConfigDesativado_path = os.path.join(base_dir, "recursos", "IconEsconderConfigDesativado.png")
            IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
            self.button.setIcon(IconesconderConfigDesativado)
            self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
            self.button.setIconSize(QtCore.QSize(50, 50))
            if self.parent() and hasattr(self.parent(), 'menu_flutuante'):
                if self.parent().menu_flutuante.jbt_esconder:
                    self.parent().menu_flutuante.jbt_esconder.hide()
                    
    def focusOutEvent(self, event):
        if not self.is_frozen:
            self.hide()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.button and (event.type() == QtCore.QEvent.TouchBegin or event.type() == QtCore.QEvent.MouseButtonPress):
            return True
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.bg_image.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def resizeEvent(self, event):
        new_size = event.size()
        width_ratio = new_size.width() / self.nova_largura
        height_ratio = new_size.height() / self.nova_altura
        self.nova_largura = int(self.original_width * width_ratio)
        self.nova_altura = int(self.original_height * height_ratio)
        self.setGeometry(self.geometry().x(), self.geometry().y(), self.nova_largura, self.nova_altura)
        self.button.setGeometry(int(319 * width_ratio), int(13 * height_ratio), int(50 * width_ratio), int(50 * height_ratio))
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = JanelaPrincipal()
    mainWindow.show()
    sys.exit(app.exec_())
