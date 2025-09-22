from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter, QIcon
import win32gui
import win32con
import sys, os

def resource_path(*paths):
    if hasattr(sys, "_MEIPASS"):
        # Quando rodar como onefile do PyInstaller
        base = sys._MEIPASS
    else:
        # Quando rodar como .exe instalado ou .py em desenvolvimento
        base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    return os.path.join(base, *paths)

class LoaderThread(QThread):
    carregamento_concluido = pyqtSignal(dict, dict)  # (sons, recursos_visuais)

    def run(self):
        # 🎵 Pré-carregar sons
        from DirigIA import carregar_sons_para_dicionario
        # Carregar sons sem instanciar JanelaPrincipal
        sons_precarregados = carregar_sons_para_dicionario(resource_path("recursos", "sons"))

        # Carregar recursos visuais normalmente
        recursos = {
            "DirigIA_White_icon": QIcon(resource_path("recursos", "DirigIA_White.ico")),
            "Background_Carro_Animado": resource_path("recursos", "Background_Carro_Animado.gif"),
            "BtIconAbrirMenu": QIcon(resource_path("recursos", "BtIconAbrirMenu.png")),
            "SomLgd_icon": QIcon(resource_path("recursos", "SomLgd.png")),
            "BtIconDesligarApp": QIcon(resource_path("recursos", "BtIconDesligarApp.png")),
            "SomDlgd_icon": QIcon(resource_path("recursos", "SomDlgd.png")),
            "BoasVindas_bg": resource_path("recursos", "boas_vindas.png"),
        }

        self.carregamento_concluido.emit(sons_precarregados, recursos)

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.7)
        self.setWindowTitle("Loading DirigIA")
        self.timer_topo = QTimer(self)
        self.timer_topo.timeout.connect(self.manter_overlay_no_topo)
        self.timer_topo.start(0)  # Reforça a cada 0ms

        QTimer.singleShot(0, self.ativar_clique_transparente)

        # 🖥️ Obtendo resolução do monitor
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📏 Calcula largura e altura com base nas margens
        margem_esq_dir = 0.2406  # 24,06%
        margem_sup_inf = 0.4308  # 43,08%

        largura_janela = int(screen_w * (1 - (margem_esq_dir * 2)))
        altura_janela  = int(screen_h * (1 - (margem_sup_inf * 2)))

        # Aplica tamanho
        self.resize(largura_janela, altura_janela)

        # 📍 Centraliza horizontal e verticalmente
        x = (screen_w - largura_janela) // 2
        y = (screen_h - altura_janela) // 2
        self.move(x, y)

        # QWebEngineView com fundo transparente
        self.web_view = QWebEngineView(self)
        self.web_view.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)

        # Depois de calcular largura_janela e altura_janela
        font_size_percent = (largura_janela / screen_w) * 10  # 10% da largura da tela original
        line_height_px = int(altura_janela * 0.45)           # 45% da altura da janela
        letter_spacing_px = int(largura_janela * 0.015)      # 1,5% da largura da janela

        html_overlay = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <title>DirigIA Overlay</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
                font-family: 'Montserrat', sans-serif;
                background: transparent;
            }}
            #dirigia-overlay {{
                position: fixed; top: 0; left: 0;
                width: 100vw; height: 100vh;
                background-image: radial-gradient(circle at 10% 20%, rgba(0,0,0,1), rgba(0,0,255,0.2));
                z-index: 999999;
                display: flex; justify-content: center; align-items: center;
                color: white; flex-direction: column;
                pointer-events: none;
            }}
            .loading-container {{
                width: 100%; max-width: 520px; text-align: center; position: relative;
                margin: 0 32px;
            }}
            .loading-container::before {{
                content: ''; position: absolute;
                width: 100%; height: 3px;
                background-color: #fff; bottom: 0; left: 0;
                border-radius: 10px;
                animation: movingLine 2.4s infinite ease-in-out;
            }}
            @keyframes movingLine {{
                0% {{ opacity: 0; width: 0; }}
                33.3%, 66% {{ opacity: 0.8; width: 100%; }}
                85% {{ width: 0; left: initial; right: 0; opacity: 1; }}
                100% {{ opacity: 0; width: 0; }}
            }}
            .loading-text {{
                font-size: {font_size_percent}vw;
                line-height: {line_height_px}px;
                letter-spacing: {letter_spacing_px}px;
                margin-bottom: 32px;
                display: flex; justify-content: space-evenly;
            }}
            .loading-text span {{
                animation: moveLetters 2.4s infinite ease-in-out;
                transform: translateX(0);
                display: inline-block;
                opacity: 0;
                text-shadow: 0px 2px 10px rgba(46, 74, 81, 0.3);
            }}
            .loading-text span:nth-child(1) {{ animation-delay: 0.1s; }}
            .loading-text span:nth-child(2) {{ animation-delay: 0.2s; }}
            .loading-text span:nth-child(3) {{ animation-delay: 0.3s; }}
            .loading-text span:nth-child(4) {{ animation-delay: 0.4s; }}
            .loading-text span:nth-child(5) {{ animation-delay: 0.5s; }}
            .loading-text span:nth-child(6) {{ animation-delay: 0.6s; }}
            .loading-text span:nth-child(7) {{ animation-delay: 0.7s; }}

            @keyframes moveLetters {{
                0% {{ transform: translateX(-15vw); opacity: 0; }}
                33.3%, 66% {{ transform: translateX(0); opacity: 1; }}
                100% {{ transform: translateX(15vw); opacity: 0; }}
            }}
        </style>
        </head>
        <body>
            <div id="dirigia-overlay">
                <div class="loading-container">
                    <div class="loading-text">
                        <span>D</span><span>i</span><span>r</span><span>i</span><span>g</span><span>I</span><span>A</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Carrega o overlay no WebView
        self.web_view.setHtml(html_overlay)

        # Inicia thread de carregamento
        QTimer.singleShot(0, self.iniciar_carregamento_janela)

    def iniciar_carregamento_janela(self):
        self.loader_thread = LoaderThread()
        self.loader_thread.carregamento_concluido.connect(self.finalizar_carregamento)
        self.loader_thread.start()

    def finalizar_carregamento(self, sons_precarregados, recursos_visuais):
        self.sons_precarregados = sons_precarregados
        self.recursos_visuais = recursos_visuais
        QTimer.singleShot(2000, self.exibir_janela_principal)

    def exibir_janela_principal(self):
        from DirigIA import JanelaPrincipal
        self.janela_principal = JanelaPrincipal(
            sons_precarregados=self.sons_precarregados,
            icones_precarregados=self.recursos_visuais,
            gif_precarregado=self.recursos_visuais.get("Background_Carro_Animado")
        )
        QTimer.singleShot(1000, lambda: (
            self.ocultar_overlay_dirigia_colab(),
            self.janela_principal.show(),
            self.boasvindas(self.janela_principal, self.recursos_visuais.get("BoasVindas_bg"))
        ))
    
    def boasvindas(self, janela_principal, bg_path):
        caminho_flag = resource_path("config.txt")
        if not os.path.exists(caminho_flag):
            dialog = BoasVindasDialog(bg_path, parent=janela_principal)
            if dialog.exec_():
                if dialog.nao_mostrar_novamente():
                    with open(caminho_flag, "w") as f:
                        f.write("Mostrar boas vindas: False")
    
    def ocultar_overlay_dirigia_colab(self):
        # print("🔕 Encerrando overlay de loading...")
        
        # 1️⃣ Parar timers para evitar que continuem rodando
        if hasattr(self, "timer_topo") and self.timer_topo.isActive():
            self.timer_topo.stop()
        
        # 2️⃣ Encerrar QThread se ainda estiver rodando
        if hasattr(self, "loader_thread") and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait()
        
        # 3️⃣ Fechar e destruir a janela
        self.hide()
        self.deleteLater()
    
        # print("✅ Overlay de loading encerrado e removido da memória.")
    
    def ativar_clique_transparente(self):

        hwnd = int(self.winId())

        # Define estilo estendido para clique-through
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        # Reforça posição no topo sem ativar
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()
        width, height = self.width(), self.height()

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            (screen_w - width) // 2,
            (screen_h - height) // 2,
            width,
            height,
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
        )

    def manter_overlay_no_topo(self):
        hwnd = int(self.winId())
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_NOREDRAW
        )

class BoasVindasDialog(QDialog):
    def __init__(self, bg_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bem-vindo ao DirigIA!")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 🖥️ Resolução do monitor
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📏 Margens
        margem_x = 0.3449
        margem_y = 0.2769
        largura_janela = int(screen_w * (1 - (margem_x * 2)))
        altura_janela  = int(screen_h * (1 - (margem_y * 2)))

        self.resize(largura_janela, altura_janela)
        self.move((screen_w - largura_janela) // 2, (screen_h - altura_janela) // 2)

        self.bg_image = QPixmap(bg_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(int(largura_janela * 0.050), int(altura_janela * 0.075),
                                  int(largura_janela * 0.050), int(altura_janela * 0.075))
        layout.setSpacing(0)

        font_label_px = max(1, int(altura_janela * 0.044)) # 4.4% da altura da janela
        texto = f"""
            <h2 style='color:black; font-size:{font_label_px}px;'>👋 Olá!</h2>
            <p style='color:black; font-size:{font_label_px}px;'>
                Seja bem-vindo ao <b>DirigIA</b>, um sistema inteligente que ajuda veículos autônomos a reconhecer objetos em tempo real.
            </p>
            <ul style='color:black; font-size:{font_label_px}px;'>
                <li>🚗 Detecta objetos com precisão</li>
                <li>🎛️ Interface fácil de usar</li>
                <li>⚙️ Perfis ajustáveis: Crítico, Essencial, Recomendado</li>
            </ul>
        """
        label = QLabel(texto)
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            font-size: {font_label_px}px;
            margin-bottom: {int(altura_janela * 0.055)}px;
        """)
        layout.addWidget(label)

        font_checkbox_px = max(1, int(altura_janela * 0.05))
        self.checkbox = QCheckBox("Não mostrar novamente")
        self.checkbox.setStyleSheet(f"""
            color: black;
            font-size: {font_checkbox_px}px;
            margin-bottom: {int(altura_janela * 0.00)}px;
        """)
        layout.addWidget(self.checkbox, alignment=Qt.AlignBottom)

        btn_w = int(largura_janela * 0.77)
        btn_h = int(altura_janela * 0.15)
        font_btn_px = max(1, int(altura_janela * 0.044))

        self.btn_ok = QPushButton("", self)
        self.btn_ok.setFixedSize(btn_w, btn_h)
        self.btn_ok.setStyleSheet(f"""
            QPushButton {{
                margin-top: {int(altura_janela * 0.00)}px;
                padding: {int(btn_h * 0.0)}px;
                background-color: rgba(0, 143, 122, 100);
                color: black;
                border-radius: {int(btn_h * 0.25)}px;
                border: 1px solid #008e9b;
            }}
        """)

        self.text_btn_ok = QLabel("CONTINUAR", self.btn_ok)
        self.text_btn_ok.setFixedSize(btn_w, btn_h)
        self.text_btn_ok.setAlignment(Qt.AlignCenter)
        self.text_btn_ok.setFont(QFont("Arial", font_btn_px, QFont.Bold))
        self.text_btn_ok.setStyleSheet("color: black;")

        shadow_effect_btn_ok = QGraphicsDropShadowEffect()
        shadow_effect_btn_ok.setColor(QColor("white"))
        shadow_effect_btn_ok.setOffset(1, 1)
        shadow_effect_btn_ok.setBlurRadius(0)
        self.text_btn_ok.setGraphicsEffect(shadow_effect_btn_ok)

        self.btn_ok.pressed.connect(lambda: (
            self.parent().reproduzirSomPreCarregado("pressionar_botao"),
            self.accept()
        ))

        layout.addWidget(self.btn_ok, alignment=Qt.AlignBottom | Qt.AlignHCenter)

    def nao_mostrar_novamente(self):
        return self.checkbox.isChecked()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.bg_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(resource_path("recursos", "DirigIA_White.ico")))
    window = OverlayWindow()
    window.show()
    app.exec_()