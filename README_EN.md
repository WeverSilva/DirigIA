# Welcome to DirigIA!

**DirigIA** is an advanced computer vision system for autonomous vehicles. It detects 21 object classes in real time through a camera while driving, using models such as **YOLOv8**. In addition to the futuristic interface built with **PyQt5**, it includes a **custom audio system with my own voice**, issuing contextual traffic alerts to enhance safety and immersion.

---

## 🔍 Overview

- **Application name:** DirigIA  
- **Theme:** Computer vision applied to autonomous vehicles.  
- **Purpose:** Increase safety and efficiency by recognizing dynamic and static objects in real time.  
- **Differential:** Multimodal interface with personalized human‑like audio and integration with Google Colab/Drive.  

---

## ✨ Key Features

- 🚗 Real‑time detection of 21 object classes via camera.  
- 🎨 Futuristic interface in PyQt5 with transparency, animations, and automated login.  
- 🔊 Custom audio with my own voice, issuing contextual traffic alerts.  
- ☁️ Integration with Google Colab/Drive for automatic storage.  
- ⚡ Focus on performance, scalability, and UX/UI.  
- 💻 Distribution with professional installer for Windows.  

---

## ⚙️ Installation

### **Requirements**
- **Python:** Version 3.x  
- **Required libraries:**  
  - PyQt5 (GUI and event control)  
  - NumPy (numerical manipulation and arrays)  
  - OpenCV (image processing)  
  - Ultralytics (training and inference with YOLOv8)  

---

## **Installation Steps**

**1. Clone the repository:**  
git clone https://github.com/WeverSilva/DirigIA.git

**2. Navigate to the project directory:** cd Loading_Overlay_DirigIA.py

**3. Install dependencies:** pip install -r requirements.txt

---

## **Download (DirigIA Installer.exe)**

- **Windows:** [Click here to download](https://drive.google.com/file/d/1UTIANeKgQbWlu81qY8NZbDP3X6rRiY0c/view?usp=sharing)

---

## 🗂️ Versions
See the full version history in [CHANGELOG.md](CHANGELOG.md).

---

## **🚀 Usage**

- **Start the application**

▪ **To run DirigIA** *(via IDE or prompt)***, use the command:** python Loading_Overlay_DirigIA.py

*( make sure you are in the app folder )*

▪ **Or open the executable:** DirigIA Installer.exe

*( available in the* **Download (DirigIA Installer.exe)** section *)*

---

## **🔧 Configuration**

- **Important Files**

  - **Dataset-PTBR_Transito_YOLOv8n.yaml:** Defines classes, image paths, and dataset structure.

  - **Trained model:** Copy the best.pt file (trained in Google Colab) to the project’s main directory.

---

## **Parameter Manipulation**

- **Operational profiles:** Use the buttons to switch between profiles:

  - **Critical:** High precision for essential objects.

  - **Recommended:** Balance between precision and speed.

  - **Essential:** Quick and simplified configuration.

  - *Profiles adjust not only precision and speed, but also the intensity of audio alerts.*

---

## **🏗️ Code Architecture**

- **Main Components**

  - **Interface/Audio:** Integration between computer vision, graphical interface, and multimodal audio system.

  - **MainWindow:** Manages GUI, animations, and states (On/Off).

  - **FloatingMenu:** Controls operational profiles and dynamic background changes.

  - **FloatingMenuConfig:** Allows advanced adjustments such as movement and system customization.

  - **JbtEsconder:** Hides the interface for optimized use on touch devices.

---

## **📊 Training**

- **Load and Use Models**

**1. Upload the best.pt file to the main directory.**

**2. Use the following code to load the model and perform inference:**

from ultralytics import YOLO
model = YOLO("best.pt")
results = model.predict(source="test_image.jpg", save=True)
print(results)

- *Compatible with datasets translated into Portuguese (PT-BR), such as COCO Dataset. Models trained in Google Colab can be loaded for real‑time inference with a camera.*

---

## 🤝 Contribution
- **How to Contribute**
*1. Fork the repository and create a branch for your changes.*

*2. Submit a pull request with a clear description of the improvements or fixes proposed.*

---

## 📜 License
- **DirigIA is licensed under the MIT License. See the LICENSE file for more information.**

---

## 📬 Contact
- **For support or questions, contact:**

  - *📧 weversonplayofcrist@gmail.com*

---

# Thank you for using DirigIA! This is an important step towards advancing autonomous vehicles with real‑time object recognition technology and multimodal accessibility. 🚗✨ Contributions are welcome to evolve this open‑source project.
