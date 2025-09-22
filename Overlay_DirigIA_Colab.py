from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QTimer
import win32gui
import win32con

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.7)
        self.setWindowTitle("Proteção de Tela do Processador")
        self.timer_topo = QTimer(self)
        self.timer_topo.timeout.connect(self.manter_overlay_no_topo)
        self.timer_topo.start(0)  # Reforça a cada 0ms
        
        QTimer.singleShot(0, self.ativar_clique_transparente)

        # 🖥️ Configurações da janela após login
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📐 Novas dimensões (39,14% largura, 82,56% altura)
        janela_w = int(screen_w * 0.3914)
        janela_h = int(screen_h * 0.8256)
        self.resize(janela_w, janela_h)

        # 📍 Posição: encostada na direita e centralizada verticalmente
        x = screen_w - janela_w
        y = int(screen_h * 0.08715)  # margem superior de 8,715%
        self.move(x, y)

        self.show()  # reaplica as flags e mostra

        # QWebEngineView com fundo transparente
        self.web_view = QWebEngineView(self)
        self.web_view.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)

        # HTML contendo o overlay animado
        html_overlay = """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>DirigIA Overlay</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
            <style>
                * { box-sizing: border-box; }
                html, body {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                    font-family: 'Montserrat', sans-serif;
                    background: transparent;
                }
                #dirigia-overlay {
                    position: fixed; top: 0; left: 0;
                    width: 100vw; height: 100vh;
                    background-image: radial-gradient(circle at 10% 20%, rgba(0,0,0,1), rgba(0,0,255,0.2));
                    z-index: 999999;
                    display: flex; justify-content: center; align-items: center;
                    color: white; flex-direction: column;
                    pointer-events: none;
                }
                .loading-container {
                    width: 100%; max-width: 520px; text-align: center; position: relative;
                    margin: 0 32px;
                }
                .loading-container::before {
                    content: ''; position: absolute;
                    width: 100%; height: 3px;
                    background-color: #fff; bottom: 0; left: 0;
                    border-radius: 10px;
                    animation: movingLine 2.4s infinite ease-in-out;
                }
                @keyframes movingLine {
                    0% { opacity: 0; width: 0; }
                    33.3%, 66% { opacity: 0.8; width: 100%; }
                    85% { width: 0; left: initial; right: 0; opacity: 1; }
                    100% { opacity: 0; width: 0; }
                }
                .loading-text {
                    font-size: 5vw; line-height: 64px;
                    letter-spacing: 10px; margin-bottom: 32px;
                    display: flex; justify-content: space-evenly;
                }
                .loading-text span {
                    animation: moveLetters 2.4s infinite ease-in-out;
                    transform: translateX(0);
                    display: inline-block;
                    opacity: 0;
                    text-shadow: 0px 2px 10px rgba(46, 74, 81, 0.3);
                }
                .loading-text span:nth-child(1) { animation-delay: 0.1s; }
                .loading-text span:nth-child(2) { animation-delay: 0.2s; }
                .loading-text span:nth-child(3) { animation-delay: 0.3s; }
                .loading-text span:nth-child(4) { animation-delay: 0.4s; }
                .loading-text span:nth-child(5) { animation-delay: 0.5s; }
                .loading-text span:nth-child(6) { animation-delay: 0.6s; }
                .loading-text span:nth-child(7) { animation-delay: 0.7s; }

                @keyframes moveLetters {
                    0% { transform: translateX(-15vw); opacity: 0; }
                    33.3%, 66% { transform: translateX(0); opacity: 1; }
                    100% { transform: translateX(15vw); opacity: 0; }
                }
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


    def ocultar_overlay_dirigia_colab(self):
        # print("🔕 Sumindo como overlay misterioso...")
        self.hide()

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
            screen_w - width,
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


if __name__ == "__main__":
    app = QApplication([])
    window = OverlayWindow()
    window.show()
    app.exec_()