# Bem-vindo à DirigIA!

O **DirigIA** é um sistema avançado de visão computacional desenvolvido para o reconhecimento de objetos em veículos autônomos. Ele utiliza técnicas de Machine Learning, modelos como o YOLOv8, e uma interface gráfica interativa para oferecer alta precisão e eficiência.

---

## 🔍 Visão Geral

- **Nome do aplicativo:** DirigIA
- **Tema:** Desenvolvimento de um sistema de visão computacional para detecção de objetos em tempo real.
- **Propósito:** Aumentar a segurança e eficiência de veículos autônomos, possibilitando o reconhecimento de objetos dinâmicos e estáticos, utilizando técnicas avançadas de Machine Learning e interfaces intuitivas.

---

## ✨ Principais Características

- **Detecção em tempo real:** Utiliza o YOLOv8 para identificar e rastrear diversos objetos com alta precisão.
- **Interface personalizada:** Desenvolvida em PyQt5, com controles interativos e animações dinâmicas.
- **Perfis adaptáveis:** Ajustes para diferentes parâmetros de detecção como **Crítico**, **Essencial** e **Recomendado**.
- **Treinamento personalizado:** Compatível com datasets traduzidos para PT-BR, como o COCO Dataset.
- **Menu flutuante:** Interface touch-friendly para configuração dinâmica.

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

**1. Clone o repositório:**
git clone https://github.com/WeverSilva/DirigIA_Interface_grafica.git
   
**2. Navegue até o diretório do projeto:**
  cd DirigIA

**3. Instale as dependências:**
  pip install -r requirements.txt

---

## **🚀 Uso**

**Iniciar o aplicativo**

**Para executar o DirigIA, use o comando:**

python DirigIA.py

---

## **🔧 Configuração**

**Arquivos Importantes**

**▫ Dataset-PTBR_Transito_YOLOv8n.yaml:** Define classes, caminhos das imagens e estrutura do dataset.

**▫ Modelo treinado:** Copie o arquivo best.pt (treinado no Google Colab) para o diretório principal do projeto.

---

## **Manipulação de Parâmetros**

**▫ Perfis operacionais:** Utilize os botões para alternar entre perfis:

  **▫ Crítico:** Alta precisão para objetos essenciais.

  **▫ Recomendado:** Equilíbrio entre precisão e velocidade.

  **▫ Essencial:** Configuração rápida e simplificada.

---

## **🏗️ Arquitetura do Código**

**Principais Componentes**

**▫ JanelaPrincipal:** Gerencia a interface gráfica, animações e estados (Ligado/Desligado).

**▫ MenuFlutuante:** Controle de perfis operacionais e alterações dinâmicas de plano de fundo.

**▫ MenuFlutuanteConfig:** Permite ajustes avançados, como movimentação e personalização do sistema.

**▫ JbtEsconder:** Esconde a interface para uso otimizado em dispositivos touch.

---

## **📊 Treinamento**

**Carregar e Usar Modelos**

**1. Suba o arquivo best.pt para o diretório principal.**

**2. Use o seguinte código para carregar o modelo e realizar inferências:**

from ultralytics import YOLO
model = YOLO("best.pt")
results = model.predict(source="test_image.jpg", save=True)
print(results)

---

## 🤝 Contribuição
**Como Contribuir**
*1. Faça o fork do repositório e crie uma ramificação para suas alterações.*

*2. Envie um pull request com uma descrição clara das melhorias ou correções propostas.*

---

## 📜 Licença
**O DirigIA está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais informações.**

---

## 📬 Contato
**Para suporte ou dúvidas, entre em contato:**

*▫ 📧 weversonplayofcrist@gmail.com*

---

# Obrigado por utilizar o DirigIA! Este é um passo importante para o avanço dos veículos autônomos com tecnologia de reconhecimento de objetos em tempo real. 🚗✨
