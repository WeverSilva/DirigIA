import os
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging"
import sys
import threading
import time
import cv2
import numpy as np
import pyautogui
import easyocr
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineScript
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import Qt, QTimer, QUrl
from Overlay_DirigIA_Colab import OverlayWindow
import win32api
import mss


# 🔹 Intercepta requisições para alterar o cabeçalho Accept-Language
class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        info.setHttpHeader(b"Accept-Language", b"pt-BR,pt;q=0.9")

# 🔸 Janela principal com navegador
class Browser(QMainWindow):
    def __init__(self, menu_flutuante=None, janela_principal=None):
        super().__init__()
        self.menu_flutuante = menu_flutuante
        self.janela_principal = janela_principal  # acesso à central sonora
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setWindowTitle("Processador do DirigIA")
        # 🖥️ Resolução física da tela
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📐 Dimensões da janela com base nas porcentagens fornecidas
        janela_w = int(screen_w * 0.2376)   # 23,76% da largura
        janela_h = int(screen_h * 0.6512)   # 65,12% da altura
        self.resize(janela_w, janela_h)

        # 📍 Posição da janela com base nas margens
        margem_esquerda = int(screen_w * 0.3812)
        margem_cima = int(screen_h * 0.1744)
        self.move(margem_esquerda, margem_cima)

        self.popups = []  # <-- lista para manter referência aos popups

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36"
        )

        # OCR Config
        self.ocr_ativo = False
        self.ocr_thread_iniciado = False
        self.overlay = None
        self.reader = easyocr.Reader(['pt'], gpu=False)
        self.run_id = 0 # Identificador único para cada ciclo de OCR
        self.detect_state = {"Conectando": {"first_seen": None, "timer": None}, "Reiniciando": {"first_seen": None, "timer": None}, "output": {"first_seen": None, "timer": None}}
        self.special = {"Conectando", "Reiniciando", "output"}
        self.palavras_alvo = ["assim", "Conectar ao Google Drive", "Aceitar", "Erro", "Falha", "Conectar", "Reconectar", "Configuração", "Conectando", "Sim", "Reiniciando", "output", "Perfil"]
        # Lista de palavras para apenas mover o cursor (sem clique)
        self.palavras_destacar = ["Conectando", "Conectar", "Reconectar", "Erro", "Falha", "Reiniciando"]
        # Lista de palavras que devem ser clicadas
        self.palavras_clicar = ["Aceitar", "Sim", "assim", "Conectar ao Google Drive", "Configuração", "output", "Perfil"]

        #WebEngine Config
        temp_profile_dir = tempfile.mkdtemp()
        self.profile = QWebEngineProfile("temporary_profile", self)
        self.profile.setPersistentStoragePath(temp_profile_dir)

        self.interceptor = RequestInterceptor()
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # 🧠 SilentPage definida dentro da classe
        class SilentPage(QWebEnginePage):
            def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
                # Ignora mensagens de JS que poluem o terminal
                if any(term in message for term in [
                    "RangeError",
                    "clipboard-write",
                    "Maximum call stack size exceeded",
                    "Failed to execute",
                    "Partial keyframes are not supported",
                    ":focus-visible",
                    "translate(0px, 0px) scale(Infinity)",
                    "Skipping recording uncaught error from XHR",
                    "Ignoring benign restart error",
                    "CustomError: Falha",
                    "Refused to load the script",
                    "Content Security Policy directive",
                    "strict-dynamic is present",
                    "Failed KXHR fetch",
                    "TypeError: Failed to fetch",
                    "No output window available",
                    "Service workers are disabled",
                    "CustomError: Timed out waiting for service worker registration",
                    "TypeError: tokens.at is not a function",
                    "handleInvoke: error name: TypeError"
                ]):
                    return
                super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

        # 🌐 Inicialização do navegador com SilentPage
        self.browser = QWebEngineView()
        self.page = SilentPage(self.profile, self.browser)
        self.browser.setPage(self.page)
        self.setCentralWidget(self.browser)
        self.page.createWindow = self.handle_popup

        # ⬅ Polyfill para structuredClone
        polyfill = QWebEngineScript()
        polyfill.setName("StructuredClonePolyfill")
        polyfill.setInjectionPoint(QWebEngineScript.DocumentCreation)
        polyfill.setRunsOnSubFrames(True)
        polyfill.setWorldId(QWebEngineScript.MainWorld)
        polyfill.setSourceCode("""
        if (typeof structuredClone === 'undefined') {
            window.structuredClone = function(obj) {
                return JSON.parse(JSON.stringify(obj));
            }
        }
        """)
        self.page.scripts().insert(polyfill)

        # 📋 Obter todos os modos de resolução de tela suportados
        modos_suportados = set()
        i = 0
        while True:
            try:
                devmode = win32api.EnumDisplaySettings(None, i)
                modos_suportados.add((devmode.PelsWidth, devmode.PelsHeight))
                i += 1
            except:
                break
            
        # 📌 Determinar resolução nativa (maior largura e altura)
        resolucao_nativa = max(modos_suportados, key=lambda m: (m[0], m[1]))
        # print(f"🧠 Resolução nativa (máxima) detectada: {resolucao_nativa[0]}x{resolucao_nativa[1]}")

        # 📌 Resolução atual
        screen = QApplication.primaryScreen().availableGeometry()
        resolucao_atual = (screen.width(), screen.height())
        # print(f"📺 Resolução atual: {resolucao_atual[0]}x{resolucao_atual[1]}")

        # 🔍 Só entra no zoom se a resolução atual for diferente da nativa
        if resolucao_atual != resolucao_nativa:
            screen_w, screen_h = resolucao_atual
            fator_zoom = 1.0
            if screen_w < 1280:      
                fator_zoom = 0.55    # 🟠 Telas SD (55%)
            elif screen_w < 1366:    
                fator_zoom = 0.7    # 🟤 SD entre HD (70%)
            elif screen_w < 1600:    
                fator_zoom = 0.75   # 🟡 HD (75%)
            elif screen_w < 1920:    
                fator_zoom = 0.9    # 🔵 Intermediárias (90%)
            elif screen_w < 2560:    
                fator_zoom = 1.0    # ⚪ Full HD (100%)
            else:                     
                fator_zoom = 1.1    # 🟢 2K, 4K ou maiores (110%)

            # Injeção de CSS zoom no DOM
            zoom_script = QWebEngineScript()
            zoom_script.setName("ForceZoomCSS")
            zoom_script.setInjectionPoint(QWebEngineScript.DocumentReady)  # após DOM pronto
            zoom_script.setRunsOnSubFrames(True)
            zoom_script.setWorldId(QWebEngineScript.MainWorld)
            zoom_script.setSourceCode(f"""
                document.documentElement.style.zoom = '{fator_zoom}';
            """)
            self.page.scripts().insert(zoom_script)

            # print(f"📏 Zoom DOM injetado: {fator_zoom}")
        else:
            pass
            # print("🖥️ Resolução atual é igual à nativa. Nenhum zoom aplicado.")

        # Conexões de sinais
        self.page.urlChanged.connect(self.verificar_login_concluido)
        self.page.featurePermissionRequested.connect(self.grant_permissions)
        self.browser.page().fullScreenRequested.connect(lambda request: request.accept())

        # 🔗 Página de autenticação inicial
        self.browser.load(QUrl("https://accounts.google.com/v3/signin/accountchooser?continue=https%3A%2F%2Fcolab.research.google.com%2Fdrive%2F1pzsjUw61oMICpkaFqQO2G7mhXV2hhqqk%3Fusp%3Dsharing&ec=GAZAqQM&flowEntry=ServiceLogin&flowName=GlifWebSignIn&hl=pt-en"))

    # Detectar saída do login
    def verificar_login_concluido(self, url):
        url_str = url.toString()
        if "accounts.google.com" not in url_str and not any(popup.isVisible() for popup in self.popups):
            # print(f"✅ Login concluído. URL atual: {url_str}")
            
            if not self.ocr_ativo and not self.ocr_thread_iniciado:
                self.ocr_ativo = True
                # print("🔄 OCR ativado após login.")
                self.iniciar_ocr_em_thread()
                self.ocr_thread_iniciado = True
                # print("🔄 Método Thread chamado.")
                QTimer.singleShot(6000, lambda: self.janela_principal.reproduzirSomPreCarregado("isso_levara_alguns_minutos"))
            else:
                if not self.ocr_ativo:
                    self.ocr_ativo = True
                    # print("🔄 OCR já tinha sido ativo, mas está sendo reativado após login.")

            # 🖥️ Configurações da janela após login
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

            # 🖥️ Obtendo resolução do monitor
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

            self.mostrar_overlay_dirigia_colab()

            # print(f"🧪 Overlay isVisible? {self.overlay.isVisible()} — isWidgetType: {self.overlay.isWidgetType()}")

        else:
            self.ocr_ativo = False
            # print(f"⛔ Ainda na tela de login: {url_str}")

    def mostrar_overlay_dirigia_colab(self):
        if not self.overlay:
            self.overlay = OverlayWindow()
            self.overlay.setAttribute(Qt.WA_QuitOnClose, False)
        self.overlay.show()
        if self.menu_flutuante:
            QTimer.singleShot(0, self.menu_flutuante.desligarDirigIA)
            # print("DirigIA foi desligado diretamente.")
    
    def ocultar_overlay_dirigia_colab(self):
        if self.overlay and self.overlay.isVisible():
            self.overlay.hide()
            # print("Overlay ocultado.")
            if self.menu_flutuante:
                QTimer.singleShot(0, self.menu_flutuante.ligarDirigIA)
                # print("Método toggleDirigIA chamado diretamente.")   

    def verificarPalavraConfirmada(self, palavra, bbox):
        """Verifica se uma palavra ainda está visível de forma consistente na tela."""
        try:
            # Resolução da tela
            screen = QApplication.primaryScreen().availableGeometry()
            screen_w, screen_h = screen.width(), screen.height()

            # Área útil igual à janela pós-login
            capture_width = int(screen_w * 0.3914)
            left = screen_w - capture_width
            top = int(screen_h * 0.08715)

            # Coordenadas absolutas da região do bbox
            (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
            region_x = left + int(x_min)
            region_y = top + int(y_min)
            region_w = int(x_max - x_min)
            region_h = int(y_max - y_min)

            # Captura da região usando mss (mais rápido que pyautogui)
            with mss.mss() as sct:
                monitor = {
                    "top": region_y,
                    "left": region_x,
                    "width": region_w,
                    "height": region_h
                }
                img = np.array(sct.grab(monitor))[:, :, :3]  # RGB

            # Nova leitura OCR
            novos_resultados = self.reader.readtext(img, detail=1, paragraph=False)
            palavra_confirmada = any(
                palavra.lower() in txt.lower().replace(" ", "")
                for _, txt, _ in novos_resultados
            )

            #print(f"Verificação de palavra '{palavra}':", "Confirmada" if palavra_confirmada else "Não confirmada")
            return palavra_confirmada

        except Exception as e:
            # print(f"Erro ao verificar a palavra '{palavra}': {e}")
            return False

    def grant_permissions(self, security_origin, feature):
        self.page.setFeaturePermission(
            security_origin,
            feature,
            QWebEnginePage.PermissionGrantedByUser
        )
    
    def iniciar_ocr_em_thread(self):
        thread = threading.Thread(target=self.loop_ocr, daemon=True)
        thread.start()
        # print("🔄 Thread de OCR iniciada.")

    def handle_popup(self, window_type):
        self.ocr_ativo = False  # ⛔ Desativa OCR assim que o popup abre

        popup = QWebEngineView()
        popup_page = QWebEnginePage(self.profile, popup)
        popup.setPage(popup_page)
        popup.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        popup.setWindowTitle("Pop-up de Autenticação")

        # 🖥️ Resolução física da tela
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 📐 Dimensões da janela com base nas porcentagens fornecidas
        janela_w = int(screen_w * 0.2376)   # 23,76% da largura
        janela_h = int(screen_h * 0.6512)   # 65,12% da altura
        popup.resize(janela_w, janela_h)

        # 📍 Posição da janela com base nas margens
        margem_esquerda = int(screen_w * 0.3812) - 50  # desloca 50px para esquerda
        margem_cima = int(screen_h * 0.1744)
        popup.move(margem_esquerda, margem_cima)

        # 📋 Obter todos os modos de resolução de tela suportados
        modos_suportados = set()
        i = 0
        while True:
            try:
                devmode = win32api.EnumDisplaySettings(None, i)
                modos_suportados.add((devmode.PelsWidth, devmode.PelsHeight))
                i += 1
            except:
                break
            
        # 📌 Determinar resolução nativa (maior largura e altura)
        resolucao_nativa = max(modos_suportados, key=lambda m: (m[0], m[1]))
        # print(f"🧠 Resolução nativa (máxima) detectada: {resolucao_nativa[0]}x{resolucao_nativa[1]}")

        # 📌 Resolução atual
        screen = QApplication.primaryScreen().availableGeometry()
        resolucao_atual = (screen.width(), screen.height())
        # print(f"📺 Resolução atual: {resolucao_atual[0]}x{resolucao_atual[1]}")

        # 🔍 Só entra no zoom se a resolução atual for diferente da nativa
        if resolucao_atual != resolucao_nativa:
            screen_w, screen_h = resolucao_atual
            fator_zoom = 1.0
            if screen_w < 1280:      
                fator_zoom = 0.55    # 🟠 Telas SD (55%)
            elif screen_w < 1366:    
                fator_zoom = 0.7    # 🟤 SD entre HD (70%)
            elif screen_w < 1600:    
                fator_zoom = 0.75   # 🟡 HD (75%)
            elif screen_w < 1920:    
                fator_zoom = 0.9    # 🔵 Intermediárias (90%)
            elif screen_w < 2560:    
                fator_zoom = 1.0    # ⚪ Full HD (100%)
            else:                     
                fator_zoom = 1.1    # 🟢 2K, 4K ou maiores (110%)

            # Injeção de CSS zoom no DOM
            zoom_script = QWebEngineScript()
            zoom_script.setName("ForceZoomCSS")
            zoom_script.setInjectionPoint(QWebEngineScript.DocumentReady)  # após DOM pronto
            zoom_script.setRunsOnSubFrames(True)
            zoom_script.setWorldId(QWebEngineScript.MainWorld)
            zoom_script.setSourceCode(f"""
                document.documentElement.style.zoom = '{fator_zoom}';
            """)
            popup_page.scripts().insert(zoom_script)

            # print(f"📏 Zoom DOM injetado: {fator_zoom}")
        else:
            pass
            # print("🖥️ Resolução atual é igual à nativa. Nenhum zoom aplicado.")

        popup_page.featurePermissionRequested.connect(
            lambda origin, feature: popup_page.setFeaturePermission(
                origin, feature, QWebEnginePage.PermissionGrantedByUser
            )
        )
        
        # 🔁 Monitorar só o popup
        def monitor_url(url):
            current_url = url.toString()
            if current_url.startswith((
                "https://colab.research.google.com/tun/m/authorize-for-drive-credentials-ephem?state=",
                "https://colab.research.google.com/tun/m/authorize-for-drive-credentials-ephem?error="
            )):
                # print(f"🔐 Autenticação concluída no popup: {current_url}")
                # ✅ Reativa OCR após fechamento do popup
                def finalizar_popup():
                    popup.close()
                    popup.setPage(None)  # desvincula a página do perfil
                    popup_page.deleteLater()  # garante que a página será destruída
                    popup.deleteLater()  # <- garante liberação de memória
                    self.popups = [p for p in self.popups if p.isVisible()]
                    self.ocr_ativo = True
                    # print("✅ Popup fechado, OCR reativado.")

                QTimer.singleShot(1000, finalizar_popup)  # Dá 1s de margem antes de fechar
                QTimer.singleShot(5000, lambda: self.janela_principal.reproduzirSomPreCarregado("esta_tudo_pronto"))
                
        popup_page.urlChanged.connect(monitor_url)

        #Visualiza URL da página⤵
        #popup_page.urlChanged.connect(lambda url: print(f"🌐 URL atual do popup: {url.toString()}"))

        self.popups.append(popup)  # <-- armazenar referência
        popup.show()
        return popup.page()

    # 🌀 OCR Loop com clique corrigido
    def loop_ocr(self):
        while True:
            if self.ocr_ativo:
                try:
                    # 🖥️ Obtendo resolução da tela principal usando PyQt5
                    screen = QApplication.primaryScreen().availableGeometry()
                    screen_width, screen_height = screen.width(), screen.height()

                    # 📐 Dimensões da área de captura (mesmas da janela pós-login)
                    capture_width = int(screen_width * 0.3914)   # 39,14% da largura
                    capture_height = int(screen_height * 0.8256) # 82,56% da altura

                    # 📍 Posição: encostada na direita e centralizada verticalmente
                    left = screen_width - capture_width
                    top = int(screen_height * 0.08715)  # margem superior de 8,715%

                    # 🖼️ Captura da região
                    screenshot = pyautogui.screenshot(region=(left, top, capture_width, capture_height))
                    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                    resultados = self.reader.readtext(img, detail=1, paragraph=False)

                    for bbox, texto, conf in resultados:
                        if not any(p.lower() in texto.lower() for p in self.palavras_alvo):
                            continue  # pula palavras não relevantes

                        texto_lower = texto.lower()  # Normalizando a palavra
                        palavra_encontrada = next((p for p in self.palavras_alvo if p.lower() in texto_lower), None)

                        # Coordenadas absolutas do clique (centro do bbox)
                        (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
                        click_x = left + int((x_min + x_max) // 2)
                        click_y = top + int((y_min + y_max) // 2)

                        if palavra_encontrada in self.palavras_destacar:
                            pyautogui.moveTo(click_x, click_y)
                            # print(f"🟢 '{palavra_encontrada}' destacado em ({click_x}, {click_y})")

                        elif palavra_encontrada in self.palavras_clicar:
                            pyautogui.click(click_x, click_y)
                            # print(f"🟢 '{palavra_encontrada}' clicada em ({click_x}, {click_y})")

                        # Se não for especial, resetamos e executamos ações imediatas:
                        if palavra_encontrada not in self.special:
                            self.run_id += 1

                            #Rotina de condições

                            if "assim" in palavra_encontrada:
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6) #Pressionará 4 vezes o botão PageDown
                                # print(f"🟢 palavra '{palavra_encontrada}' identificado! O botão Pagedown foi pressionado!")
                                continue
                            elif "Aceitar" in palavra_encontrada:
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6) #Pressionará 4 vezes o botão PageDown
                                time.sleep(1)
                                pyautogui.hotkey('ctrl', 'f9')
                                time.sleep(1)
                                pyautogui.click(click_x, click_y) # Segundo clique no mesmo ponto
                                pyautogui.press('esc', presses=3)
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6)
                                # print(f"🟢 palavra '{palavra_encontrada}' identificado! O botão Pagedown foi pressionado!")
                                continue
                            elif "Conectar ao Google Drive" in palavra_encontrada:
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6) #Pressionará 4 vezes o botão PageDown
                                # print(f"🟢 palavra '{palavra_encontrada}' identificado! O botão Pagedown foi pressionado!")
                                continue
                            elif "Configuração" in palavra_encontrada:
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6)
                                time.sleep(1)
                                pyautogui.hotkey('ctrl', 'f9')
                                time.sleep(1)
                                # print(f"🟢 Palavra '{palavra_encontrada}' identificado! Descendo a página!")
                                continue
                            elif "Erro" in palavra_encontrada:
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6)
                                time.sleep(0.1)
                                pyautogui.press('esc', presses=3)
                                pyautogui.hotkey('ctrl', 'm', 'i')
                                time.sleep(1)
                                pyautogui.press('esc', presses=3)
                                pyautogui.hotkey('ctrl', 'f9')
                                time.sleep(0.1)
                                pyautogui.press('pagedown', presses=6)
                                time.sleep(1)
                                # print(f"🟢 Palavra '{palavra_encontrada}' identificado! Descendo a página e executando todo o código do colab!")
                                continue

                            elif "Falha" in palavra_encontrada:
                                time.sleep(1)
                                pyautogui.press('pagedown', presses=6)
                                time.sleep(0.1)
                                pyautogui.press('esc', presses=3)
                                pyautogui.hotkey('ctrl', 'm', 'i')
                                time.sleep(1)
                                pyautogui.press('esc', presses=3)
                                pyautogui.hotkey('ctrl', 'f9')
                                time.sleep(0.1)
                                pyautogui.press('pagedown', presses=6)
                                time.sleep(1)
                                # print(f"🟢 Palavra '{palavra_encontrada}' identificado! Descendo a página e executando todo o código do colab!")
                                continue

                            elif "Perfil" in palavra_encontrada:

                                if not self.ocr_ativo:
                                    # print("Nenhum vestígio de palavra 'Perfil' encontrado. OCR permanece desligado.")
                                    break

                                # Captura e confirmação da palavra encontrada
                                if self.verificarPalavraConfirmada("Perfil", bbox):
                                    # print(f"🟢 'Perfil' destacado em {bbox[0]}")

                                    # Esconde o overlay
                                    QTimer.singleShot(0, self.ocultar_overlay_dirigia_colab)
                                    # print("🟢 A palavra 'Perfil' ainda está visível de forma consistente. 📷 Mostrando câmera!")

                                    # Chama o abrir_browser do MenuFlutuante, passando o bbox
                                    if self.menu_flutuante:
                                        self.menu_flutuante.bbox_perfil = bbox  # 👈 salva antes da contagem
                                        QTimer.singleShot(0, lambda: self.menu_flutuante.abrir_browser(bbox_perfil=bbox))

                                        perfil = self.menu_flutuante.last_selected_perfil
                                        if perfil == "Essencial":
                                            pyautogui.press('e')
                                            # print("🧠 Perfil 'Essencial' selecionado → pressionando tecla 'e'")
                                        elif perfil == "Recomendado":
                                            pyautogui.press('r')
                                            # print("🧠 Perfil 'Recomendado' selecionado → pressionando tecla 'r'")
                                        elif perfil == "Crítico":
                                            pyautogui.press('c')
                                            # print("🧠 Perfil 'Crítico' selecionado → pressionando tecla 'c'")

                                elif self.ocr_ativo:
                                    self.menu_flutuante.bbox_perfil = bbox  # 👈 salva antes da contagem
                                    QTimer.singleShot(0, self.mostrar_overlay_dirigia_colab)
                                    # print("🔵 A palavra 'Perfil' não foi mais detectada de forma consistente. Nenhuma ação foi tomada.")
                                else:
                                    pass
                                    # print("🚫 OCR está desligado. Nenhum overlay será mostrado.")

                                continue

                            else:
                                if "Conectar" in palavra_encontrada:
                                    time.sleep(1)
                                    pyautogui.hotkey('ctrl', 'f9')
                                    time.sleep(1)
                                    # print(f"🟢 Palavra '{palavra_encontrada}' identificado! Executar todo o código do colab!")
                                    continue

                                elif "Reconectar" in palavra_encontrada:
                                    time.sleep(1)
                                    pyautogui.hotkey('ctrl', 'f9')
                                    time.sleep(1)
                                    # print(f"🟢 Palavra '{palavra_encontrada}' identificado! Executar todo o código do colab!")
                                    continue

                        else:
                            if "Conectando" in palavra_encontrada:
                                state = self.detect_state["Conectando"]
                                now = time.time()

                                # Se é a primeira vez que aparece, registra e agenda
                                if state["first_seen"] is None:
                                    state["first_seen"] = now

                                    def confirmar_conectando(start_time=now, run_id=self.run_id, bbox_con=bbox):
                                        # Se o contexto mudou, aborta
                                        if run_id != self.run_id:
                                            # print("🟡 Confirmação de 'Conectando' abortada (reset de contexto)")
                                            self.detect_state["Conectando"] = {"first_seen": None, "timer": None}
                                            return

                                        # Se a palavra reapareceu em outro ciclo, descarta este timer
                                        if self.detect_state["Conectando"]["first_seen"] != start_time:
                                            # print("🟡 'Conectando' reapareceu, timer antigo descartado")
                                            return

                                        # print("⏳ Verificando 'Conectando' após 5s...")
                                        if self.verificarPalavraConfirmada("Conectando", bbox_con):
                                            pyautogui.press('esc', presses=3)
                                            pyautogui.hotkey('ctrl', 'm', 'i')
                                            # print("💚 'Conectando' persistiu. Reiniciando o colab.")
                                        else:
                                            pass
                                            # print("💙 'Conectando' não persistiu. Nenhuma ação.")

                                        # Limpa estado
                                        self.detect_state["Conectando"] = {"first_seen": None, "timer": None}

                                    t = threading.Timer(5.0, confirmar_conectando)
                                    state["timer"] = t
                                    t.start()
                                    # print("🟢 'Conectando' detectado. Aguardando persistência 5s.")

                                # Se já estava sendo monitorado, não reinicia o timer
                                continue
                            
                            elif "Reiniciando" in palavra_encontrada:
                                state = self.detect_state["Reiniciando"]
                                now = time.time()

                                if state["first_seen"] is None:
                                    state["first_seen"] = now

                                    def confirmar_reiniciando(start_time=now, run_id=self.run_id, bbox_rein=bbox):
                                        if run_id != self.run_id:
                                            # print("🟠 Confirmação de 'Reiniciando' abortada (reset de contexto)")
                                            self.detect_state["Reiniciando"] = {"first_seen": None, "timer": None}
                                            return

                                        if self.detect_state["Reiniciando"]["first_seen"] != start_time:
                                            # print("🟠 'Reiniciando' reapareceu, timer antigo descartado")
                                            return

                                        # print("⏳ Verificando 'Reiniciando' após 5s...")
                                        if self.verificarPalavraConfirmada("Reiniciando", bbox_rein):
                                            pyautogui.press('esc', presses=3)
                                            pyautogui.hotkey('ctrl', 'm', 'i')
                                            # print("💚 'Reiniciando' persistiu. Reiniciando o colab.")
                                        else:
                                            pass
                                            # print("💙 'Reiniciando' não persistiu. Nenhuma ação.")

                                        self.detect_state["Reiniciando"] = {"first_seen": None, "timer": None}

                                    t = threading.Timer(5.0, confirmar_reiniciando)
                                    state["timer"] = t
                                    t.start()
                                    # print("🟢 'Reiniciando' detectado. Aguardando persistência 5s.")

                                continue
                            
                            else:
                                if "output" in palavra_encontrada:
                                    state = self.detect_state["output"]
                                    now = time.time()

                                    if state["first_seen"] is None:
                                        state["first_seen"] = now

                                        def confirmar_output(start_time=now, run_id=self.run_id, bbox_out=bbox):
                                            if run_id != self.run_id:
                                                # print("🟤 Confirmação de 'output' abortada (reset de contexto)")
                                                self.detect_state["output"] = {"first_seen": None, "timer": None}
                                                return

                                            if self.detect_state["output"]["first_seen"] != start_time:
                                                # print("🟤 'output' reapareceu, timer antigo descartado")
                                                return

                                            # print("⏳ Verificando 'output' após 5s...")
                                            if self.verificarPalavraConfirmada("output", bbox_out):
                                                time.sleep(1)
                                                pyautogui.press('esc', presses=3)
                                                time.sleep(1)
                                                pyautogui.hotkey('pagedown', presses=6)
                                                time.sleep(1)
                                                pyautogui.hotkey('ctrl', 'f9')
                                                time.sleep(1)
                                                # print("💚 'output' persistiu. Reiniciando o colab.")
                                            else:
                                                pass
                                                # print("💙 'output' não persistiu. Nenhuma ação.")

                                            self.detect_state["output"] = {"first_seen": None, "timer": None}

                                        t = threading.Timer(5.0, confirmar_output)
                                        state["timer"] = t
                                        t.start()
                                        # print("🟢 'output' detectado. Aguardando persistência 5s.")

                                    continue
                                
                except Exception as e:
                    # print(f"Erro no OCR: {e}")
                    pass
            time.sleep(0.5)

# 🔹 Iniciar App + Thread OCR
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # <- ESSENCIAL
    janela = Browser()
    janela.show()

    sys.exit(app.exec_())