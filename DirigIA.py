from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QEvent, Qt, QTimer
from PyQt5.QtGui import QMouseEvent, QColor, QFont
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect
from DirigIA_Colab import Browser
from PyQt5.QtMultimedia import QSoundEffect
import pyautogui
import sys, os

def resource_path(*paths):
    if hasattr(sys, "_MEIPASS"):
        # Quando rodar como onefile do PyInstaller
        base = sys._MEIPASS
    else:
        # Quando rodar como .exe instalado ou .py em desenvolvimento
        base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.join(base, *paths)

def carregar_sons_para_dicionario(pasta_sons):
    arquivos = {
        "perfil_critico": "Perfil_critico.wav",
        "perfil_recomendado": "Perfil_recomendado.wav",
        "perfil_essencial": "Perfil_essencial.wav",
        "dirigia_ativado": "DirigIA_ativado.wav",
        "pressionar_botao": "Pressionar_botao.wav",
        "esconder_janela": "Esconder_janela.wav",
        "dirigia_desativado": "DirigIA_desativado.wav",
        "travar_destravar_janela": "Travar_destravar_janela.wav",
        "esta_tudo_pronto": "Esta_tudo_pronto.wav",
        "isso_levara_alguns_minutos": "Isso_levara_alguns_minutos.wav",
        "abrir_janela": "Abrir_janela.wav",
        "fechar_janela": "Fechar_janela.wav"
    }

    # Agora pasta_sons já é o caminho correto (ex.: resource_path("recursos", "sons"))
    sons = {chave: os.path.join(pasta_sons, nome) for chave, nome in arquivos.items()}

    # print("🔊 Caminhos dos sons pré-carregados (função utilitária).")
    return sons

class JanelaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, sons_precarregados=None, icones_precarregados=None, gif_precarregado=None):
        super().__init__()
        self.setWindowTitle("DirigIA")

        # 🔹 Sempre inicializa antes de qualquer uso
        self.sons_precarregados = sons_precarregados or {}
        self.icones_precarregados = icones_precarregados or {}
        self.gif_precarregado = gif_precarregado or {}
        self.browser_window = None
        self.sobre_mim_dialog = None

        # Sempre inicializa o atributo, mesmo que vazio
        if self.sons_precarregados and isinstance(next(iter(self.sons_precarregados.values())), str):
            sons_dict = self.sons_precarregados
            self.sons_precarregados = {}

            def criar_sons():
                for chave, caminho in sons_dict.items():
                    efeito = QSoundEffect(self)  # Agora nasce na main thread
                    efeito.setSource(QtCore.QUrl.fromLocalFile(caminho))
                    efeito.setVolume(0.9)
                    self.sons_precarregados[chave] = efeito
                # print("✅ Sons prontos na thread da GUI")

            QtCore.QTimer.singleShot(0, criar_sons)

        elif not self.sons_precarregados:
            self.precarregarSons()

        self.initUI()
        self.browser_window = None  # Controle centralizado da janela Browser
        self.jbt_esconderMf = None
        self.menu_flutuante = None
        self.last_active_button_path = None
        self.last_active_background_path = None
        self.last_dirigia_state = None
        self.SomAtvc = True

        self.installEventFilter(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    def initUI(self):
        self.showFullScreen()

        # Configuração do GIF de fundo
        if self.gif_precarregado and isinstance(self.gif_precarregado, str):
            self.bg_animation = QtGui.QMovie(self.gif_precarregado)
            # print("GIF criado na GUI thread a partir do caminho pré-carregado.")
        else:
            Background_Carro_Animado_path = resource_path("recursos", "Background_Carro_Animado.gif")
            self.bg_animation = QtGui.QMovie(Background_Carro_Animado_path)

        self.bg_label = QtWidgets.QLabel(self)
        self.bg_label.setGeometry(self.rect())
        self.bg_animation.setScaledSize(self.size())
        self.bg_label.setMovie(self.bg_animation)
        self.bg_animation.start()
        self.bg_label.lower()

        # Estado inicial
        self.last_dirigia_state = "Desligado"
        self.bg_label.show()
        self.bg_animation.stop()
        # print("BtSwtDMf está desligado. O GIF será congelado.")

        # Layout botões
        layout = QtWidgets.QVBoxLayout()

        # Botão Abrir Menu
        self.BtIconAbrirMenu = QtWidgets.QPushButton(self)
        if "BtIconAbrirMenu" in self.icones_precarregados:
            self.BtIconAbrirMenu.setIcon(self.icones_precarregados["BtIconAbrirMenu"])
            # print("✅ Ícone BtIconAbrirMenu pré-carregado usado.")
        else:
            BtIconAbrirMenu_path = resource_path("recursos", "BtIconAbrirMenu.png")
            self.BtIconAbrirMenu.setIcon(QtGui.QIcon(BtIconAbrirMenu_path))
            # print("⚠️ Ícone BtIconAbrirMenu não pré-carregado, carregando do disco.")
        self.BtIconAbrirMenu.setStyleSheet("background-color: rgba(0,0,0,0); border: solid;")
        self.BtIconAbrirMenu.setIconSize(QtCore.QSize(50, 50))
        self.BtIconAbrirMenu.setFixedSize(50, 50)
        self.BtIconAbrirMenu.pressed.connect(lambda: (
            self.reproduzirSomPreCarregado("pressionar_botao"), self.openMenuFlutuante()
        ))
        layout.addWidget(self.BtIconAbrirMenu)

        # Botão Som
        self.SomApp = QtWidgets.QPushButton(self)
        if "SomLgd_icon" in self.icones_precarregados:
            self.SomApp.setIcon(self.icones_precarregados["SomLgd_icon"])
        else:
            SomLgd_icon_path = resource_path("recursos", "SomLgd.png")
            self.SomApp.setIcon(QtGui.QIcon(SomLgd_icon_path))
        self.SomApp.setStyleSheet("background-color: rgba(0,0,0,0); border: solid;")
        self.SomApp.setIconSize(QtCore.QSize(50, 50))
        self.SomApp.setFixedSize(50, 50)
        self.SomApp.pressed.connect(self.som_interface)
        layout.addWidget(self.SomApp)

        # Botão Fechar
        self.shutdownButton = QtWidgets.QPushButton(self)
        if "BtIconDesligarApp" in self.icones_precarregados:
            self.shutdownButton.setIcon(self.icones_precarregados["BtIconDesligarApp"])
        else:
            BtIconDesligarApp_path = resource_path("recursos", "BtIconDesligarApp.png")
            self.shutdownButton.setIcon(QtGui.QIcon(BtIconDesligarApp_path))
        self.shutdownButton.setStyleSheet("background-color: rgba(0,0,0,0); border: solid;")
        self.shutdownButton.setIconSize(QtCore.QSize(50, 50))
        self.shutdownButton.setFixedSize(50, 50)
        self.shutdownButton.pressed.connect(lambda: (
            self.reproduzirSomPreCarregado("fechar_janela"),
            QTimer.singleShot(250, self.shutdownApplication)
        ))
        layout.addWidget(self.shutdownButton)

        # Botão Suporte/ Sobre Mim
        self.suporte_perfil = QtWidgets.QPushButton(self)
        if "BtIconSuportePerfil" in self.icones_precarregados:
            self.suporte_perfil.setIcon(self.icones_precarregados["BtIconSuportePerfil"])
        else:
            BtIconSuportePerfil_path = resource_path("recursos", "BtIconSuportePerfil.png")
            self.suporte_perfil.setIcon(QtGui.QIcon(BtIconSuportePerfil_path))
        self.suporte_perfil.setStyleSheet("background-color: rgba(0,0,0,0); border: solid;")
        self.suporte_perfil.setIconSize(QtCore.QSize(50, 50))
        self.suporte_perfil.setFixedSize(50, 50)
        self.suporte_perfil.pressed.connect(lambda: (self.reproduzirSomPreCarregado("pressionar_botao"), self.suportePerfil()))
        layout.addWidget(self.suporte_perfil)

        # Centraliza
        centralWidget = QtWidgets.QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def som_interface(self):
        if not self.SomAtvc:
            if "SomLgd_icon" in self.icones_precarregados:
                self.SomApp.setIcon(self.icones_precarregados["SomLgd_icon"])
            else:
                SomLgd_icon_path = resource_path("recursos", "SomLgd.png")
                self.SomApp.setIcon(QtGui.QIcon(SomLgd_icon_path))
            self.SomAtvc = True
            # print("🔊 Som da interface Ligado.")
        else:
            if "SomDlgd_icon" in self.icones_precarregados:
                self.SomApp.setIcon(self.icones_precarregados["SomDlgd_icon"])
            else:
                SomDlgd_icon_path = resource_path("recursos", "SomDlgd.png")
                self.SomApp.setIcon(QtGui.QIcon(SomDlgd_icon_path))
            self.SomAtvc = False
            # print("🔇 Som da interface Desligado.")

    def precarregarSons(self):
        pasta_sons = resource_path("recursos", "sons")
        sons = {
            "perfil_critico": "Perfil_critico.wav",
            "perfil_recomendado": "Perfil_recomendado.wav",
            "perfil_essencial": "Perfil_essencial.wav",
            "dirigia_ativado": "DirigIA_ativado.wav",
            "pressionar_botao": "Pressionar_botao.wav",
            "esconder_janela": "Esconder_janela.wav",
            "dirigia_desativado": "DirigIA_desativado.wav",
            "travar_destravar_janela": "Travar_destravar_janela.wav",
            "esta_tudo_pronto": "Esta_tudo_pronto.wav",
            "isso_levara_alguns_minutos": "Isso_levara_alguns_minutos.wav",
            "abrir_janela": "Abrir_janela.wav",
            "fechar_janela": "Fechar_janela.wav"
        }
        for chave, nome_arquivo in sons.items():
            efeito = QSoundEffect(self)
            caminho = os.path.join(pasta_sons, nome_arquivo)
            efeito.setSource(QtCore.QUrl.fromLocalFile(caminho))
            efeito.setVolume(0.9)
            self.sons_precarregados[chave] = efeito
        # print("🔊 Sons pré-carregados e prontos para uso.")

    def reproduzirSomPreCarregado(self, chave_som):
        # print(f"🔊 Tentando reproduzir som: {chave_som}")
        if self.SomAtvc and chave_som in self.sons_precarregados:
            self.sons_precarregados[chave_som].play()
        elif self.SomAtvc:
            # print(f"⚠️ Som '{chave_som}' não encontrado nos sons pré-carregados.")
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_label'):  # Verifica se bg_label foi inicializado
            self.bg_label.setGeometry(self.rect())  # Ajusta o QLabel ao tamanho da janela

    def saveLastState(self, button_path=None, background_path=None, dirigia_state=None):
        """Salva o botão ativo no QFrame ou o estado do botão BtSwtDMf.
        """
        if button_path and background_path:
            self.last_active_button_path = button_path
            self.last_active_background_path = background_path
            # print(f"Estado salvo: Botão - {self.last_active_button_path}, Plano de Fundo - {self.last_active_background_path}")

        if dirigia_state is not None:
            self.last_dirigia_state = dirigia_state
            # print(f"Estado salvo: BtSwtDMf - {self.last_dirigia_state}")

    def openMenuFlutuante(self):
        if hasattr(self, 'menu_flutuante') and self.menu_flutuante is not None:
            if self.menu_flutuante.isVisible():
                return  # Já está visível, não faz nada
            else:
                # Restaura a instância existente
                # print("🔁 Restaurando instância existente da MenuFlutuante...")
                self.menu_flutuante.show()
                self.menu_flutuante.raise_()
                self.menu_flutuante.activateWindow()
        else:
            pass
            # print("🆕 Criando nova instância da MenuFlutuante...")
            self.menu_flutuante = MenuFlutuante(self)
            self.menu_flutuante.is_frozen = False
            self.menu_flutuante.toggleFreeze()
            self.menu_flutuante.show()
            self.menu_flutuante.destroyed.connect(self.onMenuDestroyed)

        # Esconde o botão de abrir menu
        self.BtIconAbrirMenu.setVisible(False)

        # Restaura estado visual se for necessário
        if self.last_dirigia_state == "Ligado":
            self.menu_flutuante.restoreLastState(
                self.last_active_button_path, self.last_active_background_path
            )

        if self.last_active_button_path and self.last_active_background_path:
            # print(f"Restaurando último estado: Botão - {self.last_active_button_path}, Plano de Fundo - {self.last_active_background_path}")
            self.menu_flutuante.restoreLastState(self.last_active_button_path, self.last_active_background_path)
        else:
            pass
            # print("Erro: Estado anterior não encontrado.")
        self.menu_flutuante.show()

    def focusOutEvent(self, event):
        if self.is_frozen:  # Esconde apenas se o interruptor estiver ativado
            self.hide()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if self.menu_flutuante and self.menu_flutuante.isVisible():
                if self.menu_flutuante.is_frozen and not self.menu_flutuante.geometry().contains(event.globalPos()):
                    if not self.menu_flutuante.hasFocus():
                        QTimer.singleShot(0, lambda: self.reproduzirSomPreCarregado("fechar_janela"))
                        self.menu_flutuante.hide()
                        self.BtIconAbrirMenu.setVisible(True)
        return super().eventFilter(obj, event)
    
    def onMenuDestroyed(self):
        # Mostra novamente o botão
        self.BtIconAbrirMenu.setVisible(True)

    def suportePerfil(self):
        if self.sobre_mim_dialog and self.sobre_mim_dialog.isVisible():
            # print("🔁 Restaurando janela SobreMimDialog existente...")
            self.sobre_mim_dialog.raise_()
            self.sobre_mim_dialog.activateWindow()
            QtWidgets.QApplication.processEvents()
        else:
            pass
            # print("🆕 Criando nova instância de SobreMimDialog...")
            self.sobre_mim_dialog = SobreMimDialog(self)
            self.sobre_mim_dialog.show()

    def shutdownApplication(self):
        if self.browser_window and self.menu_flutuante:
            self.menu_flutuante.transferirFocoParaBrowser()
            # print("Browser focado para encerrar aplicação")
            pyautogui.click(pyautogui.size().width // 2 + pyautogui.size().width // 4, pyautogui.size().height // 2)
            pyautogui.press('esc', presses=3)
            pyautogui.hotkey('ctrl', 'm', 'i')

            self.menu_flutuante.transferirFocoParaBrowser()
            # print("Browser focado para encerrar aplicação")
            pyautogui.click(pyautogui.size().width // 2 + pyautogui.size().width // 4, pyautogui.size().height // 2)
            pyautogui.press('esc', presses=3)
            pyautogui.hotkey('ctrl', 'm', 'i')
        QTimer.singleShot(4000, QtWidgets.QApplication.quit)

class MenuFlutuante(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Referência à JanelaPrincipal
        self.last_background = None  # Inicializa a variável para evitar erros
        self.last_active_button = None  # Variável para o botão ativo
        self.bbox_perfil = None
        self.menu_flutuante_config = None  # Inicializa como None
        self.jbt_esconder = None  # Inicializa como None
        self.is_frozen = True  # Variável para controlar o estado de congelamento
        self.offset = None  # Armazena a posição inicial do clique/touch
        self.bg_label = None
        self.bg_animation = None
        self.last_selected_perfil = None
        self.efeito_sonoro = QSoundEffect(self)
        self.initUI()
        
    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)     

        # Carregar a imagem de fundo
        Menu_flutuante_path = resource_path("recursos", "Menu_flutuante.png")
        self.bg_image = QtGui.QPixmap(Menu_flutuante_path)

        # 🖥️ Resolução da tela
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📏 Margens proporcionais
        margem_x = 0.3971  # 39,61% esquerda/direita
        margem_y = 0.1205  # 11,69% cima/baixo

        # 📐 Tamanho da janela com base nas margens
        largura_janela = int(screen_w * (1 - margem_x * 2))
        altura_janela  = int(screen_h * (1 - margem_y * 2))

        # 📍 Posição centralizada
        pos_x = int(screen_w * 0.1)  # 10% da largura da tela
        pos_y = (screen_h - altura_janela) // 2  # Centralizado verticalmente

        # 🪟 Aplicar geometria
        self.setGeometry(pos_x, pos_y, largura_janela, altura_janela)

        # Guardar dimensões base para cálculo proporcional
        self.base_w = largura_janela
        self.base_h = altura_janela

        # 🔘 Botão DirigIA (proporcional à janela)
        self.BtSwtDMf = QtWidgets.QPushButton("", self)
        self.BtSwtDMf.setGeometry(
            int(largura_janela * (270 / self.base_w)),   # 270px → 71% da largura base original
            int(altura_janela * (40 / self.base_h)),    # 40px  → 5% da altura base original
            int(largura_janela * (100 / self.base_w)),   # 100px → 26% da largura base original
            int(altura_janela * (100 / self.base_h))    # 100px → 12,5% da altura base original
        )
        # Inicia com o estado "Desligado"
        self.BtSwtDMf.state = False  # False = Desligado, True = Ligado
        BtSwtDMfDlgd_path = resource_path("recursos", "BtSwtDMfDlgd.png")
        BtSwtDMfDlgd = QtGui.QIcon(BtSwtDMfDlgd_path)
        self.BtSwtDMf.setIcon(BtSwtDMfDlgd)
        self.BtSwtDMf.setStyleSheet("""QPushButton {background-color: rgba(0, 0, 0, 0); text-align: right;}""")
        # Ícone proporcional ao tamanho real da janela
        icon_w = int(largura_janela * 0.22)   # 22% da largura da janela
        icon_h = int(altura_janela * 0.22)    # 22% da altura da janela
        self.BtSwtDMf.setIconSize(QtCore.QSize(icon_w, icon_h))
        self.BtSwtDMf.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("pressionar_botao"), self.confirmStateChange()))

        # Botão para esconder a janela
        self.buttonesconder = QtWidgets.QPushButton("", self)
        self.buttonesconder.setGeometry(
            int(largura_janela * (319 / self.base_w)),
            int(altura_janela * (13 / self.base_h)),
            int(largura_janela * (50 / self.base_w)),
            int(altura_janela * (50 / self.base_h))
        )
        IconEsconderConfigDesativado_path = resource_path("recursos", "IconEsconderConfigDesativado.png")
        IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
        self.buttonesconder.setIcon(IconesconderConfigDesativado)
        self.buttonesconder.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: solid;")
        # Ícone proporcional ao tamanho real da janela
        icon_w = int(largura_janela * 0.13)   # 50px em relação à largura base (~11%)
        icon_h = int(altura_janela * 0.13)    # 50px em relação à altura base (~11%)
        self.buttonesconder.setIconSize(QtCore.QSize(icon_w, icon_h))
        self.buttonesconder.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("travar_destravar_janela"), self.toggleFreeze()))

        # Ajustar a proporção do botão
        self.button = QtWidgets.QPushButton("", self)
        self.button.setGeometry(
            int(largura_janela * (40 / self.base_w)),
            int(altura_janela * (433 / self.base_h)),
            int(largura_janela * (290 / self.base_w)),
            int(altura_janela * (70 / self.base_h))
        )
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        # Conectar eventos de toque e clique ao botão
        self.button.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("abrir_janela"), self.openNewFloatingWindow()))

        # Criação do QFrame dentro da classe
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(
            int(largura_janela * (6 / self.base_w)),
            int(altura_janela * (624 / self.base_h)),
            int(largura_janela * (380 / self.base_w)),
            int(altura_janela * (160 / self.base_h))
        )
        self.frame.setStyleSheet("background-color: rgba(0, 0, 0, 0); border-radius: 10px;")  # Remove cor de fundo padrão

        # Botões e seus nomes associados
        self.BtPfCritiMf = QtWidgets.QPushButton("", self.frame)
        self.BtPfRecoMf = QtWidgets.QPushButton("", self.frame)
        self.BtPfEssenMf = QtWidgets.QPushButton("", self.frame)
        self.BtPfCritiMf.setObjectName("Crítico")
        self.BtPfRecoMf.setObjectName("Recomendado")
        self.BtPfEssenMf.setObjectName("Essencial")

        # Imagens associadas aos botões
        self.icons = {
            "Crítico": resource_path("recursos", "BtPfCritiMf.png"),
            "Recomendado": resource_path("recursos", "BtPfRecoMf.png"),
            "Essencial": resource_path("recursos", "BtPfEssenMf.png"),
        }
        # Configuração inicial dos botões
        self.BtPfCritiMf.setGeometry(
            int(largura_janela * (250 / self.base_w)),
            int(altura_janela * (0 / self.base_h)),
            int(largura_janela * (128 / self.base_w)),
            int(altura_janela * (160 / self.base_h))
        )
        self.BtPfCritiMf.setStyleSheet(self.buttonStyle())
        self.BtPfCritiMf.pressed.connect(lambda: self.handleCustomClick(self.BtPfCritiMf))

        self.BtPfRecoMf.setGeometry(
            int(largura_janela * (126 / self.base_w)),
            int(altura_janela * (0 / self.base_h)),
            int(largura_janela * (128 / self.base_w)),
            int(altura_janela * (160 / self.base_h))
        )
        self.BtPfRecoMf.setStyleSheet(self.buttonStyle())
        self.BtPfRecoMf.pressed.connect(lambda: self.handleCustomClick(self.BtPfRecoMf))

        self.BtPfEssenMf.setGeometry(
            int(largura_janela * (2 / self.base_w)),
            int(altura_janela * (0 / self.base_h)),
            int(largura_janela * (128 / self.base_w)),
            int(altura_janela * (160 / self.base_h))
        )
        self.BtPfEssenMf.setStyleSheet(self.buttonStyle())
        self.BtPfEssenMf.pressed.connect(lambda: self.handleCustomClick(self.BtPfEssenMf))
    
    def handleCustomClick(self, button):
        """Lida com cliques nos botões BtPfCritiMf, BtPfRecoMf e BtPfEssenMf com base no estado do BtSwtDMf.
        """
        self.last_selected_perfil = button.objectName()

        # 🔊 Reproduz som específico conforme botão, com segurança na thread principal
        if button == self.BtPfCritiMf:
            QTimer.singleShot(0, lambda: self.parent_window.reproduzirSomPreCarregado("perfil_critico"))
        elif button == self.BtPfRecoMf:
            QTimer.singleShot(0, lambda: self.parent_window.reproduzirSomPreCarregado("perfil_recomendado"))
        elif button == self.BtPfEssenMf:
            QTimer.singleShot(0, lambda: self.parent_window.reproduzirSomPreCarregado("perfil_essencial"))

        if not self.BtSwtDMf.state:  # BtSwtDMf está Desligado
            # print(f"BtSwtDMf está Desligado. Ativando e destacando o botão correspondente: {button.objectName()}.")

            # Exibe o perfil_frame (contagem regressiva)
            self.showPerfilFrame(button)

            # Destaca o botão clicado
            self.highlightButton(button.objectName())

            # Simula cliques reais no botão clicado
            # print("Chamando simulateClicks...")
            self.simulateClicks(button)
        else:    # BtSwtDMf está Ativado
            # print(f"BtSwtDMf está Ativado. Executando a ação diretamente para {button.objectName()}.")
            self.changeBackground(button.objectName())  # Segue diretamente para alterar o fundo

    def buttonStyle(self):
        """Retorna o estilo dos botões com transparência e bordas destacadas.
        """
        return (
            "background-color: rgba(0, 0, 0, 0);"
            "border-radius: 10px;"
        )
    def changeBackground(self, button_name):
        """Alterar o plano de fundo do QFrame conforme o botão selecionado.
        """
        image_path = self.icons.get(button_name)  # Busca o caminho da imagem pelo nome do botão
        # print(f"Alterando plano de fundo para: {image_path}")

        if not image_path or not QtCore.QFile.exists(image_path):  # Verifica se o caminho é válido
            # print(f"Erro: Caminho inválido ou inexistente - {image_path}")
            return
        self.last_background = image_path
        self.last_active_button = button_name

        self.parent_window.saveLastState(button_name, image_path)
        # Aplicar o plano de fundo no QFrame
        self.applyBackground(image_path)
        self.highlightButton(button_name)
    
    def highlightButton(self, button_name):
        """Destaca o botão clicado e redefine o estilo dos demais.
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
        """Aplica o plano de fundo ao QFrame.
        """
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            # print(f"Erro: O QPixmap não conseguiu carregar a imagem - {image_path}")
            return

        # print(f"Aplicando plano de fundo: {image_path}")
        scaled_pixmap = pixmap.scaled(
            self.frame.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        palette = self.frame.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(scaled_pixmap))
        self.frame.setPalette(palette)
        self.frame.setAutoFillBackground(True)
        self.frame.update()
        self.frame.repaint()

    def restoreLastState(self, button_name=None, background_path=None):
        """Restaura o último botão ativo e aplica seu plano de fundo (do QFrame).
        Também restaura o estado do botão BtSwtDMf.
        """
        last_state = self.parent_window.last_dirigia_state
        if last_state == "Ligado":
            BtSwtDMfLgd_path = resource_path("recursos", "BtSwtDMfLgd.png")
            BtSwtDMfLgd = QtGui.QIcon(BtSwtDMfLgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfLgd)
            self.BtSwtDMf.state = True
            #QTimer.singleShot(3000, lambda: self.parent_window.reproduzirSomPreCarregado("dirigia_ativado"))
            # print("BtSwtDMf restaurado para: Ligado")
        else:
            BtSwtDMfDlgd_path = resource_path("recursos", "BtSwtDMfDlgd.png")
            BtSwtDMfDlgd = QtGui.QIcon(BtSwtDMfDlgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfDlgd)
            self.BtSwtDMf.state = False
            #QTimer.singleShot(0, lambda: self.parent_window.reproduzirSomPreCarregado("dirigia_desativado"))
            # print("BtSwtDMf restaurado para: Desligado")
            return

        # Restaurar o último botão ativo do QFrame
        if button_name and background_path:
            # print(f"Restaurando botão: {button_name}, Plano de fundo: {background_path}")
            self.applyBackground(background_path)
            self.highlightButton(button_name)

            if not background_path or not QtCore.QFile.exists(background_path):
                # print(f"Erro: Caminho da imagem inválido ou inexistente - {background_path}")
                return

            # Aplicar plano de fundo e destacar o botão
            self.applyBackground(background_path)
            self.highlightButton(button_name)

    def show(self):
        """Mostra a janela.
        """
        super().show()

    def toggleFreeze(self):
        self.is_frozen = not self.is_frozen

        # 🖥️ Resolução da tela
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📏 Margens proporcionais
        margem_x = 0.3961  # 39,61% esquerda/direita
        margem_y = 0.1169  # 11,69% cima/baixo

        # 📐 Tamanho da janela com base nas margens
        largura_janela = int(screen_w * (1 - margem_x * 2))
        altura_janela  = int(screen_h * (1 - margem_y * 2))

        if self.is_frozen:
            IconEsconderConfigAtivado_path = resource_path("recursos", "IconEsconderConfigAtivado.png")
            IconesconderConfigAtivado = QtGui.QIcon(IconEsconderConfigAtivado_path)
            self.buttonesconder.setIcon(IconesconderConfigAtivado)
            self.buttonesconder.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: solid;")
            # Ícone proporcional ao tamanho real da janela
            icon_w = int(largura_janela * 0.13)   # 50px em relação à largura base (~11%)
            icon_h = int(altura_janela * 0.13)    # 50px em relação à altura base (~11%)
            self.buttonesconder.setIconSize(QtCore.QSize(icon_w, icon_h))
        else:
            IconEsconderConfigDesativado_path = resource_path("recursos", "IconEsconderConfigDesativado.png")
            IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
            self.buttonesconder.setIcon(IconesconderConfigDesativado)
            self.buttonesconder.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: solid;")
            # Ícone proporcional ao tamanho real da janela
            icon_w = int(largura_janela * 0.13)   # 50px em relação à largura base (~11%)
            icon_h = int(altura_janela * 0.13)    # 50px em relação à altura base (~11%)
            self.buttonesconder.setIconSize(QtCore.QSize(icon_w, icon_h))

    def fonteAdaptativa(self, proporcao_altura, height_ratio, minimo=5):
        tamanho = max(int(self.base_h * proporcao_altura * height_ratio), minimo)
        return QFont("Arial", tamanho, QFont.Weight.Bold)

    def paddingAdaptativo(self, proporcao_altura, height_ratio, minimo=5):
        return max(int(self.base_h * proporcao_altura * height_ratio), minimo)
    
    def confirmStateChange(self):
        """Mostra um alerta com 80% de transparência antes de mudar o estado do botão BtSwtDMf.
        Agora, os elementos visíveis (contador e botão cancelar) estão dentro de um QFrame.
        """
        largura_janela = self.width()
        altura_janela = self.height()

        # Proporção atual em relação à base
        width_ratio = largura_janela / self.base_w
        height_ratio = altura_janela / self.base_h

        self.BtSwtDMf.setEnabled(False)
        self.alert_dialog = QtWidgets.QDialog(self)

        # Definir a janela como transparente, mantendo os elementos visíveis dentro do QFrame
        self.alert_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.alert_dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.alert_dialog.setStyleSheet("background-color: transparent; border: none;")

        # Criando um QFrame dentro do QDialog para isolar os elementos visíveis
        self.local_frame = QtWidgets.QFrame(self)
        self.local_frame.setGeometry(
            int(self.base_w * 0.590 * width_ratio),   # X = 231 / base_w
            int(self.base_h * 0.392 * height_ratio),  # Y = 323 / base_h
            int(self.base_w * 0.415 * width_ratio),   # W = 170 / base_w
            int(self.base_h * 0.160 * height_ratio)   # H = 130 / base_h
        )

        self.local_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0); border-radius: 15px;")  # Apenas o QFrame será visível

        # Criando um layout para organizar os elementos dentro do QFrame
        layout = QtWidgets.QVBoxLayout(self.local_frame)

        # Configuração do contador regressivo
        self.countdown_label = QtWidgets.QLabel("5", self.local_frame)
        self.countdown_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(self.fonteAdaptativa(0.03, height_ratio, 5))   # 5% da altura base, mínimo 5px
        # Configuração do botão cancelar
        self.cancel_button_BtSwt = QtWidgets.QPushButton("CANCELAR", self.local_frame)
        self.cancel_button_BtSwt.setFont(self.fonteAdaptativa(0.017, height_ratio, 5))  # 3% da altura base, mínimo 5px
        padding_top = self.paddingAdaptativo(0.020, height_ratio, 6)   # 2% da altura base
        padding_bottom = self.paddingAdaptativo(0.020, height_ratio, 6)

        self.cancel_button_BtSwt.setStyleSheet(f"""
            QPushButton {{
                padding-top: {padding_top}px;
                padding-bottom: {padding_bottom}px;
                font-weight: bold;
                background-color: rgba(0, 143, 122, 0.3);
                color: black;
                border-radius: 10px;
                border: 1px solid #008e9b;
            }}
        """)

        # Aplicar o efeito de contorno ao texto
        shadow_effect_CancelBtSwt = QGraphicsDropShadowEffect()
        shadow_effect_CancelBtSwt.setColor(QColor("white"))  # Cor do contorno
        shadow_effect_CancelBtSwt.setOffset(-1, -1)             # Sem deslocamento
        shadow_effect_CancelBtSwt.setBlurRadius(0)           # Raio do desfoque
        self.cancel_button_BtSwt.setGraphicsEffect(shadow_effect_CancelBtSwt)
        self.cancel_button_BtSwt.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("esconder_janela"), self.cancelStateChange()))

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

    def updateCountdown(self, bbox_perfil=None):
        """Atualiza a contagem regressiva dentro do alerta.
        """
        # print("🧠 Verificando bbox_perfil:", self.bbox_perfil)

        if self.remaining_time > 1:
            self.remaining_time -= 1
            self.countdown_label.setText(str(self.remaining_time))
        else:
            self.timer.stop()
            if self.local_frame.isVisible():  # Verifica se o QFrame está visível
                self.local_frame.close()
                self.alert_dialog.close()
                self.BtSwtDMf.setEnabled(True)

                if self.bbox_perfil and self.parent_window.browser_window.verificarPalavraConfirmada("Perfil", self.bbox_perfil):
                    self.parent_window.browser_window.hide()
                    # print("💫Ocultando a janela Browser após confirmação do clique.")
                    self.desligarDirigIA()  # Desliga o DirigIA
                    # print("❌Desligando DirigIA após confirmação do clique.")
                    self.parent_window.browser_window.ocr_ativo = False
                    # print("🔌 OCR desligado com sucesso.")
                    return
                else:   
                    # Agendando a abertura da janela Browser na thread principal
                    QTimer.singleShot(0, lambda: self.abrir_browser(bbox_perfil=self.bbox_perfil))
                    # print("🚪 janela Browser após contagem regressiva.")
        
    def abrir_browser(self, bbox_perfil=None):
        """ Abre a janela Browser, verificando se já existe uma instância visível.
        Se não
        """
        if hasattr(self.parent_window, 'browser_window') and self.parent_window.browser_window is not None:
            if self.parent_window.browser_window.isVisible():
                # print("🔁 Janela Browser já está visível. Apenas restaurando...")
                self.parent_window.browser_window.raise_()
                self.parent_window.browser_window.activateWindow()

                if self.bbox_perfil and not self.parent_window.browser_window.ocr_ativo:
                    self.parent_window.browser_window.ocr_ativo = True
                    # print("🔌 OCR não estava ativo. Ativando agora...")

                perfil_desejado = self.last_selected_perfil
                botao_real = self.getPerfilButton(perfil_desejado)
                if botao_real and bbox_perfil:

                    self.BtSwtDMf.state = True
                    BtSwtDMfLgd_path = resource_path("recursos", "BtSwtDMfLgd.png")
                    self.BtSwtDMf.setIcon(QtGui.QIcon(BtSwtDMfLgd_path))

                    # print(f"✅ Palavra 'Perfil' confirmada. Ativando DirigIA e perfil {perfil_desejado}.")

                    self.highlightButton(perfil_desejado)
                    self.changeBackground(perfil_desejado)
                    self.ativar_Perfil(botao_real)
                    self.simulateClicks(botao_real)
                    self.transferirFocoParaBrowser()
                else:
                    if bbox_perfil:
                        self.ligarDirigIA()  # Liga o DirigIA se necessário
                        # print("🆗 Gráfico e status do botão")
                    else:
                        pass
                        # print("❌ Nenhum gráfico registrado. Gráfico não será ativado.")
            else:
                pass
                # print("🔁 Janela Browser já existe, mas está oculta. Restaurando...")
                self.parent_window.browser_window.show()
                self.parent_window.browser_window.raise_()
                self.parent_window.browser_window.activateWindow()

                if self.bbox_perfil and not self.parent_window.browser_window.ocr_ativo:
                    self.parent_window.browser_window.ocr_ativo = True
                    # print("🔌 OCR não estava ativo. Ativando agora...")
                
                perfil_desejado = self.last_selected_perfil
                botao_real = self.getPerfilButton(perfil_desejado)
                if botao_real and bbox_perfil:

                    self.BtSwtDMf.state = True
                    BtSwtDMfLgd_path = resource_path("recursos", "BtSwtDMfLgd.png")
                    self.BtSwtDMf.setIcon(QtGui.QIcon(BtSwtDMfLgd_path))

                    # print(f"✅ Palavra 'Perfil' confirmada. Ativando DirigIA e perfil {perfil_desejado}.")

                    self.highlightButton(perfil_desejado)
                    self.changeBackground(perfil_desejado)
                    self.ativar_Perfil(botao_real)
                    self.simulateClicks(botao_real)
                    self.transferirFocoParaBrowser()
                else:
                    if bbox_perfil:
                        self.ligarDirigIA()  # Liga o DirigIA se necessário
                        # print("🆗 Gráfico e status do botão")
                    else:
                        pass
                        # print("❌ Nenhum gráfico registrado. Gráfico não será ativado.")
        else:
            pass
            # print("🆕 Criando nova instância da janela Browser...")
            self.parent_window.browser_window = Browser(menu_flutuante=self, janela_principal=self.parent_window)
            self.parent_window.browser_window.show()

    def cancelStateChange(self):
        """Cancela a alteração do estado do botão BtSwtDMf e fecha o QFrame.
        """
        self.timer.stop()
        if self.local_frame.isVisible():  # Verifica se o QFrame está visível
            self.local_frame.close()
            self.alert_dialog.close()
            self.BtSwtDMf.setEnabled(True)
        # print("Alteração cancelada pelo usuário.")

    def getPerfilButton(self, nome):
        mapping = {
            "Crítico": self.BtPfCritiMf,
            "Recomendado": self.BtPfRecoMf,
            "Essencial": self.BtPfEssenMf,
        }
        return mapping.get(nome)
    
    def transferirFocoParaBrowser(self):
        self.show()
        self.raise_()
        self.activateWindow()
        QtWidgets.QApplication.processEvents()
        # print("Transferindo foco para a janela Browser...")

        if self.parent_window and hasattr(self.parent_window, "browser_window"):
            self.parent_window.browser_window.raise_()
            self.parent_window.browser_window.activateWindow()
            # print("Foco transferido para a janela Browser.")
            QtWidgets.QApplication.processEvents()
    
    def ligarDirigIA(self):
        perfil_desejado = getattr(self, "last_selected_perfil", None)
        botao_real = self.getPerfilButton(perfil_desejado)

        if botao_real and self.parent_window.browser_window.verificarPalavraConfirmada("Perfil", self.bbox_perfil):

            self.BtSwtDMf.state = True
            BtSwtDMfLgd_path = resource_path("recursos", "BtSwtDMfLgd.png")
            self.BtSwtDMf.setIcon(QtGui.QIcon(BtSwtDMfLgd_path))

            # print(f"✅ Palavra 'Perfil' confirmada. Ativando DirigIA e perfil {perfil_desejado}.")

            self.highlightButton(perfil_desejado)
            self.changeBackground(perfil_desejado)
            self.ativar_Perfil(botao_real)
            self.simulateClicks(botao_real)
            self.transferirFocoParaBrowser()

        else:
            pass
            # print("⚠️ Palavra não confirmada ou perfil não registrado corretamente.")
            if not self.BtSwtDMf.state:
                self.toggleDirigIA()
                self.transferirFocoParaBrowser()

    def desligarDirigIA(self):
        if self.BtSwtDMf.state:
            self.toggleDirigIA()
            self.transferirFocoParaBrowser()
    
    def toggleDirigIA(self):
        """Alterna o estado do botão BtSwtDMf entre "Desligado" e "Ligado".
        """
        if not self.BtSwtDMf.state:  # Estado atual é Desligado
            # Mudança para "Ligado"
            BtSwtDMfLgd_path = resource_path("recursos", "BtSwtDMfLgd.png")
            BtSwtDMfLgd = QtGui.QIcon(BtSwtDMfLgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfLgd)
            self.BtSwtDMf.state = True  # Atualiza o estado para Ligado
            self.parent_window.saveLastState(None, None, "Ligado")
            QTimer.singleShot(3000, lambda: self.parent_window.reproduzirSomPreCarregado("dirigia_ativado"))
            # print("BtSwtDMf: DirigIA Ligado")
    
            # Agora acessamos o GIF de fundo corretamente
            if hasattr(self.parent_window, "bg_label") and hasattr(self.parent_window, "bg_animation"):
                self.parent_window.bg_label.show()
                self.parent_window.bg_animation.start()
                # print("BtSwtDMf está ligado. O GIF será exibido.")
            else:
                pass
                # print("Erro: bg_label ou bg_animation não encontrados na JanelaPrincipal.")
    
            # Simula dois cliques reais no botão BtPfRecoMf
            # print("Chamando simulateClicks...")
            self.simulateClicks(self.BtPfRecoMf)
            self.restoreLastState()

        else:
            # Mudança para "Desligado"
            BtSwtDMfDlgd_path = resource_path("recursos", "BtSwtDMfDlgd.png")
            BtSwtDMfDlgd = QtGui.QIcon(BtSwtDMfDlgd_path)
            self.BtSwtDMf.setIcon(BtSwtDMfDlgd)
            self.BtSwtDMf.state = False  # Atualiza o estado para Desligado
            self.parent_window.saveLastState(None, None, "Desligado")
            # print("BtSwtDMf: DirigIA Desligado")
            QTimer.singleShot(0, lambda: self.parent_window.reproduzirSomPreCarregado("dirigia_desativado"))
    
            # Atualiza o estado global
            self.parent_window.last_dirigia_state = "Ligado" if self.BtSwtDMf.state else "Desligado"
            # print(f"Estado salvo: BtSwtDMf - {'Ligado' if self.BtSwtDMf.state else 'Desligado'}")
    
            # Restaura o estado inicial dos botões do QFrame
            self.resetQFrameButtons()
    
            # Agora acessamos o GIF de fundo corretamente
            if hasattr(self.parent_window, "bg_label") and hasattr(self.parent_window, "bg_animation"):
                self.parent_window.bg_animation.stop()
                # print("BtSwtDMf está desligado. O GIF será congelado.")
            else:
                pass
                # print("Erro: bg_label ou bg_animation não encontrados na JanelaPrincipal.")     
            self.restoreLastState()

    def showPerfilFrame(self, button):
        """Exibe um QDialog chamado perfil_frame com contagem regressiva e mensagem personalizada.
        """
        largura_janela = self.width()
        altura_janela = self.height()

        # Proporção atual em relação à base
        width_ratio = largura_janela / self.base_w
        height_ratio = altura_janela / self.base_h

        if self.BtSwtDMf.state:  # Botão está ativado
            # print(f"BtSwtDMf está ativado. Continuando para o método changeBackground com o botão {button.objectName()}.")
            self.changeBackground(button.objectName())  # Executa o método changeBackground normalmente
            return

        #Desabilitar os botões
        self.BtPfCritiMf.setEnabled(False)
        self.BtPfRecoMf.setEnabled(False)
        self.BtPfEssenMf.setEnabled(False)
        self.BtSwtDMf.setEnabled(False)
        # print("Botões desabilitados após o clique.")

        # Criando o QDialog
        self.perfil_frame = QtWidgets.QDialog(self)

        # Configuração do QDialog
        self.perfil_frame.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.perfil_frame.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.perfil_frame.setStyleSheet("background-color: transparent; border: none;")
        self.perfil_frame.setFixedSize(
            int(self.base_w * 0.366 * width_ratio),   # W = 300 / base_w
            int(self.base_h * 0.222 * height_ratio)   # H = 200 / base_h
        )

        #Criando um Qframe dentro do QDialog para isolar os elementos visíveis
        self.frame_perfil = QtWidgets.QFrame(self)
        self.frame_perfil.setGeometry(
            int(self.base_w * 0.001 * width_ratio),   # X = 1 / base_w
            int(self.base_h * 0.629 * height_ratio),  # Y = 518 / base_h
            int(self.base_w * 0.998 * width_ratio),   # W = 396 / base_w
            int(self.base_h * 0.374 * height_ratio)   # H = 310 / base_h
        )
        self.frame_perfil.setStyleSheet("background-color: rgba(0, 0, 0, 0); border-radius: 15px;")  # Apenas o QFrame será visível

        # Configuração do layout interno
        layout = QtWidgets.QVBoxLayout(self.perfil_frame)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margens

        # Mensagem personalizada
        self.perfil_frame_label2 = QtWidgets.QLabel(f"                         {button.objectName()}\n               Ativando DirigIA ...", self.frame_perfil)
        self.perfil_frame_label2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignBottom)
        self.perfil_frame_label2.setFont(self.fonteAdaptativa(0.020, height_ratio, 5))  # 13% da altura base, mínimo 5px
        self.perfil_frame_label2.setGeometry(
            int(self.base_w * 0.000 * width_ratio),
            int(self.base_h * 0.000 * height_ratio),  # Y = -5 / base_h
            int(self.base_w * 0.481 * width_ratio),
            int(self.base_h * 0.070 * height_ratio)
        )
        shadow_effectTxPf = QGraphicsDropShadowEffect()
        shadow_effectTxPf.setColor(QColor("white"))   #Cor do contorno
        shadow_effectTxPf.setOffset(1, -1)   #Sem deslocamento
        shadow_effectTxPf.setBlurRadius(0) #Raio do desfoque para o contorno
        self.perfil_frame_label2.setGraphicsEffect(shadow_effectTxPf)
        #self.perfil_frame_label2.show()

        # Contador regressivo
        self.perfil_countdown_label = QtWidgets.QLabel("5", self.perfil_frame)
        self.perfil_countdown_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignBottom)
        self.perfil_countdown_label.setFont(self.fonteAdaptativa(0.03, height_ratio, 5)) # 20% da altura base, mínimo 5px
        shadow_effect_contador_perfil = QGraphicsDropShadowEffect()
        shadow_effect_contador_perfil.setColor(QColor("white"))  # Cor do contorno
        shadow_effect_contador_perfil.setOffset(1, -1)             # Sem deslocamento
        shadow_effect_contador_perfil.setBlurRadius(0)           # Raio do desfoque
        self.perfil_countdown_label.setGraphicsEffect(shadow_effect_contador_perfil)

        # Criar o botão CANCELAR
        self.cancel_perfil = QtWidgets.QPushButton("                            CANCELAR                            ", self.perfil_frame)
        self.cancel_perfil.setFont(self.fonteAdaptativa(0.017, height_ratio, 5))  # 3% da altura base, mínimo 5px
        padding_top = self.paddingAdaptativo(0.020, height_ratio, 6)   # 2% da altura base
        padding_bottom = self.paddingAdaptativo(0.020, height_ratio, 6)
        self.cancel_perfil.setStyleSheet(f"""
            QPushButton {{
                padding-top: {padding_top}px;
                padding-bottom: {padding_bottom}px;
                font-weight: bold;
                background-color: rgba(0, 143, 122, 0.3);
                color: black;
                border-radius: 10px;
                border: 1px solid #008e9b;
            }}
        """)

        # Aplicar o efeito de contorno ao texto
        shadow_effect_cancel_perfil = QGraphicsDropShadowEffect()
        shadow_effect_cancel_perfil.setColor(QColor("white"))  # Cor do contorno
        shadow_effect_cancel_perfil.setOffset(1, -1)             # Sem deslocamento
        shadow_effect_cancel_perfil.setBlurRadius(0)           # Raio do desfoque
        self.cancel_perfil.setGraphicsEffect(shadow_effect_cancel_perfil)
        self.cancel_perfil.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("esconder_janela"), self.cancelStatePerfil()))
        
        # Adicionando os elementos ao layout
        layout.addWidget(self.perfil_frame_label2)
        layout.addWidget(self.cancel_perfil, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
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
        """Atualiza a contagem regressiva do perfil_frame.
        Após o término:
        - Ativa automaticamente o botão BtSwtDMf chamando toggleDirigIA.
        - Seleciona e destaca o botão correspondente ao clique (BtPfCritiMf, BtPfRecoMf, BtPfEssenMf).
        """
        if self.perfil_remaining_time > 1:
            self.perfil_remaining_time -= 1
            self.perfil_countdown_label.setText(str(self.perfil_remaining_time))
        else:
            # Agendando a abertura da janela Browser na thread principal
            QTimer.singleShot(0, lambda: self.abrir_browser(bbox_perfil=self.bbox_perfil))
            # print("🚪 janela Browser após contagem regressiva.")
            self.perfil_timer.stop()
            if self.frame_perfil.isVisible():  #Verifica se o frame está visível
                self.frame_perfil.close()
                self.perfil_frame.close()
                # print("perfil_frame fechado após a contagem regressiva.")
            # Reabilitar os botões
            self.BtPfCritiMf.setEnabled(True)
            self.BtPfRecoMf.setEnabled(True)
            self.BtPfEssenMf.setEnabled(True)
            self.BtSwtDMf.setEnabled(True)
            # print("Botões reabilitados após a contagem regressiva.")

    def ativar_Perfil(self, button):
        # Mudança para "Ligado"
        BtSwtDMfLgd_path = resource_path("recursos", "BtSwtDMfLgd.png")
        BtSwtDMfLgd = QtGui.QIcon(BtSwtDMfLgd_path)
        self.BtSwtDMf.setIcon(BtSwtDMfLgd)
        self.BtSwtDMf.state = True  # Atualiza o estado para Ligado
        self.parent_window.saveLastState(None, None, "Ligado")
        QTimer.singleShot(3000, lambda: self.parent_window.reproduzirSomPreCarregado("dirigia_ativado"))
        # print("BtSwtDMf: DirigIA Ligado")

        # Agora acessamos o GIF de fundo corretamente
        if hasattr(self.parent_window, "bg_label") and hasattr(self.parent_window, "bg_animation"):
            self.parent_window.bg_label.show()
            self.parent_window.bg_animation.start()
            # print("BtSwtDMf está ligado. O GIF será exibido.")
        else:
            pass
            # print("Erro: bg_label ou bg_animation não encontrados na JanelaPrincipal.")
        
        # Destaca o botão clicado
        # print(f"Destacando o botão correspondente: {button.objectName()}")
        self.highlightButton(button.objectName())
        #Simula os cliques no botão correspondente
        # print(f"Chamando simulateClicksperfil para {button.objectName()}.")
        self.simulateClicksperfil(button)
       
    def cancelStatePerfil(self):
        self.perfil_timer.stop()
        if self.frame_perfil.isVisible():
            self.frame_perfil.close()
            self.perfil_frame.close()
            # print("Alteração de perfil realizada pelo usuário!")
            # Reabilitar os botões
            self.BtPfCritiMf.setEnabled(True)
            self.BtPfRecoMf.setEnabled(True)
            self.BtPfEssenMf.setEnabled(True)
            self.BtSwtDMf.setEnabled(True)

    def resetQFrameButtons(self):
        """Restaura o estado inicial dos botões do QFrame (nenhum botão selecionado).
        """
        self.BtPfCritiMf.setStyleSheet(self.buttonStyle())
        self.BtPfRecoMf.setStyleSheet(self.buttonStyle())
        self.BtPfEssenMf.setStyleSheet(self.buttonStyle())

        # Remove o plano de fundo aplicado no QFrame
        self.frame.setAutoFillBackground(False)
        self.frame.update()
        # print("Botões do QFrame restaurados ao estado inicial.")

    def simulateClicks(self, button, num_clicks=2):
        if button is None or not button.isVisible():
            # print(f"Erro: O botão {button.objectName() if button else 'None'} não está disponível para clique.")
            return

        # print(f"Entrou em simulateClicks para o botão {button.objectName()}")

        center_point = QtCore.QPointF(button.rect().center())

        for _ in range(num_clicks):
            # print(f"Simulando clique em {center_point}")
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.Type.MouseButtonPress,
                    center_point,
                    center_point,
                    center_point,
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.LeftButton,
                    Qt.KeyboardModifier.NoModifier
                )
            )
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.Type.MouseButtonRelease,
                    center_point,
                    center_point,
                    center_point,
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.NoButton,
                    Qt.KeyboardModifier.NoModifier
                )
            )
            # print(f"Simulação de clique real realizada no botão {button.objectName()}.")

    def simulateClicksperfil(self, button, num_clicks=2):
        if button is None or not button.isVisible():
            # print(f"Erro: O botão {button.objectName() if button else 'None'} não está disponível para clique.")
            return

        # print(f"Entrou em simulateClicksperfil para o botão {button.objectName()}")

        center_point = QtCore.QPointF(button.rect().center())

        for _ in range(num_clicks):
            # print(f"Simulando clique em {center_point}")
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.Type.MouseButtonPress,
                    center_point,
                    center_point,
                    center_point,
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.LeftButton,
                    Qt.KeyboardModifier.NoModifier
                )
            )
            QApplication.postEvent(
                button,
                QMouseEvent(
                    QEvent.Type.MouseButtonRelease,
                    center_point,
                    center_point,
                    center_point,
                    Qt.MouseButton.LeftButton,
                    Qt.MouseButton.NoButton,
                    Qt.KeyboardModifier.NoModifier
                )
            )
            # print(f"Simulação de clique real realizada no botão {button.objectName()}.")

        # Chamar changeBackground após simulação
        self.changeBackground(button.objectName())

    def resizeEvent(self, event):
        new_size = event.size()
        largura_janela = self.width()
        altura_janela = self.height()

        # Proporção atual em relação à base
        width_ratio = largura_janela / self.base_w
        height_ratio = altura_janela / self.base_h

        # 🔘 BtSwtDMf
        self.BtSwtDMf.setGeometry(
            int(self.base_w * 0.098 * width_ratio),   # X = 270 / base_w
            int(self.base_h * 0.384 * height_ratio),  # Y = 40 / base_h
            int(self.base_w * 0.758 * width_ratio),   # W = 100 / base_w
            int(self.base_h * 0.100 * height_ratio)   # H = 100 / base_h
        )

        # 🔘 Botão esconder
        self.buttonesconder.setGeometry(
            int(self.base_w * 0.84 * width_ratio),   # X = 319 / base_w
            int(self.base_h * 0.017 * height_ratio),  # Y = 13 / base_h
            int(self.base_w * 0.14 * width_ratio),   # W = 50 / base_w
            int(self.base_h * 0.050 * height_ratio)   # H = 50 / base_h
        )

        # 🔘 Botão principal
        self.button.setGeometry(
            int(self.base_w * 0.099 * width_ratio),   # X = 40 / base_w
            int(self.base_h * 0.516 * height_ratio),  # Y = 433 / base_h
            int(self.base_w * 0.754 * width_ratio),   # W = 290 / base_w
            int(self.base_h * 0.100 * height_ratio)   # H = 70 / base_h
        )

        # 📦 Frame principal
        self.frame.setGeometry(
            int(self.base_w * 0.000 * width_ratio),   # X = 6 / base_w
            int(self.base_h * 0.744 * height_ratio),  # Y = 624 / base_h
            int(self.base_w * 0.997 * width_ratio),   # W = 380 / base_w
            int(self.base_h * 0.228 * height_ratio)   # H = 160 / base_h
        )

        # 🔘 Botões de perfil
        self.BtPfCritiMf.setGeometry(
            int(self.base_w * 0.667 * width_ratio),   # X = 250 / base_w
            int(self.base_h * 0.000 * height_ratio),  # Y = 0
            int(self.base_w * 0.329 * width_ratio),   # W = 128 / base_w
            int(self.base_h * 0.228 * height_ratio)   # H = 160 / base_h
        )

        self.BtPfRecoMf.setGeometry(
            int(self.base_w * 0.338 * width_ratio),   # X = 126 / base_w
            int(self.base_h * 0.000 * height_ratio),
            int(self.base_w * 0.329 * width_ratio),
            int(self.base_h * 0.228 * height_ratio)
        )

        self.BtPfEssenMf.setGeometry(
            int(self.base_w * 0.010 * width_ratio),   # X = 2 / base_w
            int(self.base_h * 0.000 * height_ratio),
            int(self.base_w * 0.329 * width_ratio),
            int(self.base_h * 0.228 * height_ratio)
        )

        # Atualiza tamanho dos ícones
        self.BtSwtDMf.setIconSize(QtCore.QSize(
            int(largura_janela * 0.22),
            int(altura_janela * 0.22)
        ))

        self.buttonesconder.setIconSize(QtCore.QSize(
            int(largura_janela * 0.13),
            int(altura_janela * 0.13)
        ))

        super().resizeEvent(event)

    def paintEvent(self, event):
        """Método para desenhar o plano de fundo personalizado.
        """
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.bg_image.scaled(self.size(), QtCore.Qt.AspectRatioMode.IgnoreAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))

    def focusOutEvent(self, event):
        """Esconde a janela ao perder o foco, caso o interruptor esteja desligado.
        """
        if not self.is_frozen:
            self.hide()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        """Evento chamado ao pressionar o botão do mouse.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.offset = event.pos()  # Armazena a posição inicial do clique

    def mouseMoveEvent(self, event):
        """Evento chamado ao mover o mouse enquanto o botão esquerdo está pressionado.
        """
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPos() - self.offset
            self.move(delta)

    def mouseReleaseEvent(self, event):
        """Evento chamado ao soltar o botão do mouse.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.offset = None  # Reseta o deslocamento quando o clique for solto

    def touchEvent(self, event):
        """Captura eventos de toque no caso de dispositivos touch.
        """
        if event.type() == QtCore.QEvent.Type.TouchBegin:
            self.offset = event.pos()
        elif event.type() == QtCore.QEvent.Type.TouchUpdate and self.offset is not None:
            delta = event.globalPos() - self.offset
            self.move(delta)
        elif event.type() == QtCore.QEvent.Type.TouchEnd:
            self.offset = None  # Reseta ao finalizar o toque

    def openNewFloatingWindow(self):
        """Abre janelas flutuantes adicionais, como perfis e configurações.
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
        """Esconde a janela ao perder o foco, caso o interruptor esteja desligado.
        """
        if not self.is_frozen:
            self.hide()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        """Filtra eventos específicos relacionados ao botão principal.
        """
        if obj == self.button and (event.type() == QtCore.QEvent.Type.TouchBegin or event.type() == QEvent.Type.MouseButtonPress):
            return True
        return super().eventFilter(obj, event)

class JbtEsconder(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Referência à JanelaPrincipal
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())

        self.bt_esconder = QtWidgets.QPushButton(self)
        self.bt_esconder.setGeometry(0, 0, self.width(), self.height())
        self.bt_esconder.setStyleSheet("background-color: rgba(255, 0, 0, 0.0); border: solid;")
        self.bt_esconder.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("fechar_janela"), self.hideMenuFlutuanteConfig()))

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
        self.parent_window = parent  # Referência à JanelaPrincipal

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

        # Carregar a imagem de fundo
        Menu_flutuante_Config_path = resource_path("recursos", "Menu_flutuante_Config.png")
        self.bg_image = QtGui.QPixmap(Menu_flutuante_Config_path)

        # 🖥️ Resolução da tela
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📐 Dimensões da janela com base nas porcentagens fornecidas
        self.base_w = int(screen_w * 0.20)   # 20% da largura
        self.base_h = int(screen_h * 0.60)   # 60% da altura
        self.resize(self.base_w, self.base_h)

        # 📍 Posição da janela com base nas margens (exemplo: centralizada)
        margem_esquerda = int(screen_w * 0.40)
        margem_cima = int(screen_h * 0.20)
        self.move(margem_esquerda, margem_cima)

        # Ajustar a proporção do botão
        self.button = QtWidgets.QPushButton("", self)
        self.button.setGeometry(
            int(self.base_w * (319 / self.base_w)),
            int(self.base_h * (13 / self.base_h)),
            int(self.base_w * (50 / self.base_w)),
            int(self.base_h * (50 / self.base_h))
        )
        IconEsconderConfigDesativado_path = resource_path("recursos", "IconEsconderConfigDesativado.png")
        IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
        self.button.setIcon(IconesconderConfigDesativado)
        self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
        icon_w = int(self.base_w * 0.13)
        icon_h = int(self.base_h * 0.13)
        self.button.setIconSize(QtCore.QSize(icon_w, icon_h))
        # Conectar eventos de toque e clique ao botão
        self.button.pressed.connect(lambda: (self.parent_window.reproduzirSomPreCarregado("travar_destravar_janela"), self.toggleFreeze()))

    # Adicione os métodos de movimentação abaixo:
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.offset = event.pos()  # Armazena a posição inicial do clique

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPos() - self.offset
            self.move(delta)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.offset = None  # Reseta o deslocamento quando o clique for solto

    def touchEvent(self, event):
        # Captura eventos de toque no caso de dispositivos touch
        if event.type() == QtCore.QEvent.Type.TouchBegin:
            self.offset = event.pos()
        elif event.type() == QtCore.QEvent.Type.TouchUpdate and self.offset is not None:
            delta = event.globalPos() - self.offset
            self.move(delta)
        elif event.type() == QtCore.QEvent.Type.TouchEnd:
            self.offset = None  # Reseta ao finalizar o toque

    def toggleFreeze(self):

        icon_w = int(self.width() * 0.13)
        icon_h = int(self.height() * 0.13)

        self.is_frozen = not self.is_frozen  # Alternar o estado
        if self.is_frozen:
            # Configuração para estado ativado
            IconEsconderConfigAtivado_path = resource_path("recursos", "IconEsconderConfigAtivado.png")
            IconesconderConfigAtivado = QtGui.QIcon(IconEsconderConfigAtivado_path)
            self.button.setIcon(IconesconderConfigAtivado)
            self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
            self.button.setIconSize(QtCore.QSize(icon_w, icon_h))
            if self.parent() and hasattr(self.parent(), 'menu_flutuante'):
                if self.parent().menu_flutuante.jbt_esconder:
                    self.parent().menu_flutuante.jbt_esconder.show()
        else:
            # Configuração para estado desativado
            IconEsconderConfigDesativado_path = resource_path("recursos", "IconEsconderConfigDesativado.png")
            IconesconderConfigDesativado = QtGui.QIcon(IconEsconderConfigDesativado_path)
            self.button.setIcon(IconesconderConfigDesativado)
            self.button.setStyleSheet("background-color: rgba(0, 0, 0, 0.0); border: solid;")
            self.button.setIconSize(QtCore.QSize(icon_w, icon_h))
            if self.parent() and hasattr(self.parent(), 'menu_flutuante'):
                if self.parent().menu_flutuante.jbt_esconder:
                    self.parent().menu_flutuante.jbt_esconder.hide()
                    
    def focusOutEvent(self, event):
        if not self.is_frozen:
            self.hide()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.button and (event.type() == QtCore.QEvent.Type.TouchBegin or event.type() == QEvent.Type.MouseButtonPress):
            return True
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.bg_image.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        new_size = event.size()
        largura_janela = new_size.width()
        altura_janela = new_size.height()

        width_ratio = largura_janela / self.base_w
        height_ratio = altura_janela / self.base_h

        # Atualiza botão proporcionalmente
        self.button.setGeometry(
            int(self.base_w * 0.839 * width_ratio),
            int(self.base_h * -0.110 * height_ratio),
            int(self.base_w * 0.131 * width_ratio),
            int(self.base_h * 0.312 * height_ratio)
        )

        icon_w = int(largura_janela * 0.13)
        icon_h = int(altura_janela * 0.13)
        self.button.setIconSize(QtCore.QSize(icon_w, icon_h))

        super().resizeEvent(event)
    
class SobreMimDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre o Criador")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 🖥️ Obter resolução da tela
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📐 Calcular tamanho da janela com base nas margens
        window_w = int(screen_w * 0.4)  # 40% largura
        window_h = int(screen_h * 0.6)  # 60% altura
        pos_x = int((screen_w - window_w) / 2)
        pos_y = int((screen_h - window_h) / 2)

        # 🪟 Aplicar tamanho e posição
        self.setGeometry(pos_x, pos_y, window_w, window_h)

        # 🎨 Imagem de fundo redimensionada
        bg_path = resource_path("recursos", "sobre_mim.png")
        self.bg_image = QtGui.QPixmap(bg_path)

        # 🔹 Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 🔝 TOPO FIXO: Foto + Título
        topo_widget = QtWidgets.QWidget()
        topo_layout = QtWidgets.QVBoxLayout(topo_widget)
        topo_layout.setContentsMargins(0, 0, 0, 0)

        # Foto
        foto = QtWidgets.QLabel()
        foto_path = resource_path("recursos", "BtIconSuportePerfil.png")
        pixmap = QtGui.QPixmap(foto_path)
        foto.setPixmap(pixmap.scaled(int(window_w * 0.2), int(window_w * 0.2), QtCore.Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topo_layout.addWidget(foto)

        # Título
        titulo = QtWidgets.QLabel("<h2 style='color:black; font-weight:normal; font-size: 26px;'>Sou <b>Weverson</b></h2>")
        titulo.setTextFormat(QtCore.Qt.TextFormat.RichText)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topo_layout.addWidget(titulo)

        main_layout.addWidget(topo_widget)

        # 🔄 Área de rolagem
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: rgba(0, 0, 0, 0); border-radius: 10px; font-size: 26px;")

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)

        font_label_px = max(1, int(window_h * 0.044))  # Tamanho da fonte proporcional à altura da janela
        # Texto com HTML e links
        texto = QtWidgets.QLabel(f"""
            <p style="color:black; font-size:{font_label_px}px;">
                Criador do <b>DirigIA</b>, apaixonado por inteligência artificial e visão computacional.<br><br>
                Minha trajetória nesse projeto começou enquanto trabalhava na fábrica da Stellantis, em Goiana-PE, onde tive contato direto com tecnologias automotivas e inovação industrial. Essa experiência despertou meu interesse por sistemas inteligentes e me inspirou a desenvolver, como Trabalho de Conclusão de Curso em Sistemas de Informação, o projeto <b>DirigIA</b>, uma solução de visão computacional para reconhecimento de objetos em tempo real em veículos autônomos.<br><br>
                Confira meus projetos:
            </p>
            <ul>
                <li><a href="https://github.com/WeverSilva">GitHub</a></li>
            </ul>
        """)
        texto.setOpenExternalLinks(True)
        texto.setWordWrap(True)
        content_layout.addWidget(texto)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # 🔘 Botão Fechar com redimensionamento proporcional
        btn_fechar = QtWidgets.QPushButton("", self)
        btn_fechar.setFixedSize(int(window_w * 0.4), int(window_h * 0.1))  # 40% largura da janela, 10% altura
        btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 143, 122, 100);
                border-radius: 10px;
                border: 1px solid #008e9b;
            }
        """)

        self.text_btn_fechar = QtWidgets.QLabel("FECHAR", btn_fechar)
        self.text_btn_fechar.setFixedSize(btn_fechar.size())
        self.text_btn_fechar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_btn_fechar.setFont(QtGui.QFont("Arial", int(window_h * 0.03), QtGui.QFont.Weight.Bold))  # Tamanho da fonte proporcional
        self.text_btn_fechar.setStyleSheet("color: black;")
        self.text_btn_fechar.setFixedSize(btn_fechar.size())

        shadow_effect_btn_fechar = QGraphicsDropShadowEffect()
        shadow_effect_btn_fechar.setColor(QColor("white"))
        shadow_effect_btn_fechar.setOffset( 1, 1)
        shadow_effect_btn_fechar.setBlurRadius(0)
        self.text_btn_fechar.setGraphicsEffect(shadow_effect_btn_fechar)

        btn_fechar.pressed.connect(lambda: (
            self.parent() and self.parent().reproduzirSomPreCarregado("fechar_janela"),
            self.close()
        ))

        main_layout.addSpacing(15)  # Espaço de 15 pixels entre o texto e o botão
        main_layout.addWidget(btn_fechar, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(
            0, 0,
            self.bg_image.scaled(
                self.size(),
                QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,  # 🔄 Ajusta sem preservar proporção
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
        )

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = JanelaPrincipal()
    mainWindow.show()
    sys.exit(app.exec())