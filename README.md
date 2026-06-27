🌐 Leia também em [English](README_EN.md)

# Bem-vindo à DirigIA!

O **DirigIA** é um sistema avançado de visão computacional para veículos autônomos. Detecta em tempo real 21 classes de objetos através de uma câmera durante a condução, utilizando modelos como o **YOLOv8**. Além da interface futurista em **PyQt5**, inclui um **sistema de áudio personalizado com minha voz**, que emite alertas contextuais do trânsito para aumentar segurança e imersão.

---

## 🔍 Visão Geral

- **Nome do aplicativo:** DirigIA
- **Tema:** Visão computacional aplicada a veículos autônomos.
- **Propósito:** Aumentar a segurança e eficiência, reconhecendo objetos dinâmicos e estáticos em tempo real.
- **Diferencial:** Interface multimodal com áudio humano personalizado e integração com Google Colab/Drive.

---

## ✨ Principais Características

- 🚗 Detecção em tempo real de 21 classes de objetos via câmera.
- 🎨 Interface futurista em PyQt5 com transparência, animações e automação de login.
- 🔊 Áudio personalizado com minha voz, emitindo alertas contextuais do trânsito.
- ☁️ Integração com Google Colab/Drive para armazenamento automático.
- ⚡ Foco em desempenho, escalabilidade e UX/UI.
- 💻 Distribuição com instalador profissional para Windows.

---

## ⚙️ Instalação

### **Requisitos**
- **Python:** Versão 3.x
- **Bibliotecas necessárias:**
  - PyQt5 (Interface gráfica e controle de eventos)
  - NumPy (Manipulação numérica e arrays)
  - OpenCV (Processamento de imagens)
  - Ultralytics (Treinamento e inferência com YOLOv8)

---

## **Etapas de Instalação**

**1. Clone o repositório:** git clone https://github.com/WeverSilva/DirigIA.git
   
**2. Navegue até o diretório do projeto:** cd Loading_Overlay_DirigIA.py

**3. Instale as dependências:** pip install -r requirements.txt

---

## **Download (Instalador DirigIA.exe)**

- **Windows:** [Clique aqui para baixar](https://drive.google.com/file/d/1UTIANeKgQbWlu81qY8NZbDP3X6rRiY0c/view?usp=sharing)

---

## 🗂️ Versões
Veja o histórico completo de versões em [CHANGELOG.md](CHANGELOG.md).

---

## **🚀 Uso**

- **Iniciar o aplicativo**

▪ **Para executar o DirigIA** *(via IDE ou prompt)***, use o comando:** python Loading_Overlay_DirigIA.py

*( certifique que esteja na pasta do app )*

▪ **Ou Abra o executável:** Instalador DirigIA.exe

*( disponível na sessão* **download (Instalador DirigIA.exe)** *)*

---

## **🔧 Configuração**

- **Arquivos Importantes**

  - **Dataset-PTBR_Transito_YOLOv8n.yaml:** Define classes, caminhos das imagens e estrutura do dataset.

  - **Modelo treinado:** Copie o arquivo best.pt (treinado no Google Colab) para o diretório principal do projeto.

---

## **Manipulação de Parâmetros**

- **Perfis operacionais:** Utilize os botões para alternar entre perfis:

  - **Crítico:** Alta precisão para objetos essenciais.

  - **Recomendado:** Equilíbrio entre precisão e velocidade.

  - **Essencial:** Configuração rápida e simplificada.

  - *Perfis ajustam não apenas precisão e velocidade, mas também intensidade dos alertas sonoros.*

---

## **🏗️ Arquitetura do Código**

- **Principais Componentes**

  - **Interface/Áudio:** Integração entre visão computacional, interface gráfica e sistema de áudio multimodal.

  - **JanelaPrincipal:** Gerencia a interface gráfica, animações e estados (Ligado/Desligado).

  - **MenuFlutuante:** Controle de perfis operacionais e alterações dinâmicas de plano de fundo.

  - **MenuFlutuanteConfig:** Permite ajustes avançados, como movimentação e personalização do sistema.

  - **JbtEsconder:** Esconde a interface para uso otimizado em dispositivos touch.

---

## **📊 Treinamento**

- **Carregar e Usar Modelos**

**1. Suba o arquivo best.pt para o diretório principal.**

**2. Use o seguinte código para carregar o modelo e realizar inferências:**

from ultralytics import YOLO
model = YOLO("best.pt")
results = model.predict(source="test_image.jpg", save=True)
print(results)

- *Compatível com datasets traduzidos para PT-BR, como COCO Dataset. Modelos treinados no Google Colab podem ser carregados para inferência em tempo real com câmera.*

---

## 🤝 Contribuição
- **Como Contribuir**
*1. Faça o fork do repositório e crie uma ramificação para suas alterações.*

*2. Envie um pull request com uma descrição clara das melhorias ou correções propostas.*

---

## 📜 Licença
- **O DirigIA está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais informações.**

---

## 📬 Contato
- **Para suporte ou dúvidas, entre em contato:**

  - *📧 weversonplayofcrist@gmail.com*

---

# Obrigado por utilizar o DirigIA! Este é um passo importante para o avanço dos veículos autônomos com tecnologia de reconhecimento de objetos em tempo real. 🚗✨ Contribuições são bem-vindas para evoluir este projeto open source.
