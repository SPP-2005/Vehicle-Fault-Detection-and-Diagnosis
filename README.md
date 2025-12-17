# 🚗 Intelligent Vehicle Fault Diagnosis System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Model-orange)
![Frontend](https://img.shields.io/badge/Frontend-Glassmorphism-purple)

## 📋 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [Model Performance](#-model-performance)
- [Future Scope](#-future-scope)
- [Contributors](#-contributors)

---

## 📖 About the Project

The **Intelligent Vehicle Fault Diagnosis System** is a machine learning-based web application designed to move vehicle maintenance from a *reactive* approach to a *predictive* one.

By analyzing live sensor data (such as Engine Temperature, RPM, Oil Pressure, and Vibration Levels), the system can:
1.  **Detect** if a fault exists.
2.  **Diagnose** the specific type of fault (e.g., Overheating, Worn Brakes).
3.  **Identify** the faulty component unit (e.g., Cooling System, Brake System).
4.  **Estimate** the severity of the fault (Score 1-10).

This project aims to reduce vehicle breakdowns, lower maintenance costs, and improve road safety using a **Hierarchical Random Forest** approach.

---

## ✨ Key Features

* **Real-Time Diagnosis:** Instant analysis of sensor inputs.
* **Two-Stage Prediction:** First checks for faults, then performs deep diagnosis only if needed.
* **Severity Estimation:** Provides a regression-based severity score to prioritize repairs.
* **Modern UI:** A responsive, "Glassmorphism" design interface built with HTML/CSS/JS.
* **Context Aware:** Accounts for ambient temperature and vehicle age during analysis.

---

## 🏗 System Architecture

The project uses a **Hierarchical Model Architecture**:

1.  **Stage 1: Fault Detection Model (Binary Classification)**
    * Determines if the vehicle is "Faulty" or "Not Faulty".
    * *Algorithm:* Random Forest Classifier.

2.  **Stage 2: Diagnosis Models (Multi-Class & Regression)**
    * Activates *only* if a fault is detected in Stage 1.
    * **Fault Type Model:** Predicts the specific issue (e.g., "Fuel Injector Clog").
    * **Fault Unit Model:** Predicts the system origin (e.g., "Fuel System").
    * **Severity Model:** Predicts a risk score (1.0 - 10.0).

---

## 🛠 Tech Stack

### Backend & Machine Learning
* **Python:** Core programming language.
* **Flask:** Web framework for serving the API.
* **Scikit-Learn:** Model training and evaluation.
* **Pandas & NumPy:** Data manipulation and preprocessing.
* **Joblib:** Model persistence (saving/loading models).

### Frontend
* **HTML5:** Page structure.
* **CSS3:** Styling (Gradient backgrounds, Glassmorphism effects).
* **JavaScript (Vanilla):** API communication and DOM manipulation.

---

## 📂 Project Structure

```text
Vehicle Fault Detection Project/
│
├── data/
│   └── vehicle_fault_data_v9.csv        # The dataset used for training
│
├── models/                              # Serialized ML models
│   ├── Vehicle_Fault_Detection_Model.pkl
│   ├── Vehicle_Fault_Diagnosis_Model.pkl
│   ├── Vehicle_Fault_Unit_Model.pkl
│   ├── Vehicle_Fault_Severity_Model.pkl
│   └── scaler.joblib                    # Saved StandardScaler for preprocessing
│
├── notebooks/
│   └── Vehicle Fault Detection.ipynb    # Jupyter Notebook for training
│
├── web_app/                             # The Flask Application
│   ├── static/
│   │   ├── style.css                    # CSS Styling
│   │   └── script.js                    # Logic to fetch API
│   ├── templates/
│   │   └── index.html                   # Main UI Page
│   └── app.py                           # Flask Backend Server
│
└── README.md

## ⚙ Installation & Setup

Follow these steps to run the project locally.

### Prerequisites
* Python 3.8 or higher installed.

### Step 1: Clone or Download
Download the project folder to your local machine.

### Step 2: Install Dependencies
Open your terminal or command prompt and run the following command to install the required libraries:

```bash
pip install flask flask-cors pandas numpy scikit-learn joblib
```

### Step 3: Run the Application
Navigate to the `web_app` directory and start the Flask server:

```bash
cd web_app
python app.py
```

You should see output indicating the server is running:
`Running on http://127.0.0.1:5000`

---

## 🚀 Usage

1.  Open your web browser and go to **`http://127.0.0.1:5000`**.
2.  You will see the **Intelligent Vehicle Fault Diagnosis** dashboard.
3.  Select the **Car Brand** and **Model**.
4.  Use the sliders to simulate sensor readings (e.g., increase `Engine Temp`, lower `Coolant Level`).
5.  Click the **"Diagnose Vehicle"** button.
6.  The system will process the data and display the results on the right side of the screen.

---

## 📊 Model Performance

| Model | Metric | Score |
| :--- | :--- | :--- |
| **Detection Model** | Accuracy | 94% |
| **Detection Model** | Precision (Fault Class) | 1.00 (Zero False Positives) |
| **Diagnosis (Type)** | F1-Score | 98% |
| **Diagnosis (Unit)** | F1-Score | 98% |
| **Severity (Regressor)**| R-Squared | 0.85 |

*Note: The Detection Model prioritizes Precision to ensure that users are not alerted unless a fault is genuinely present.*

---

## 🔮 Future Scope

* **Mobile App Integration:** Porting the frontend to React Native or Flutter.
* **Multi-Label Classification:** Detecting multiple simultaneous faults (e.g., Worn Brakes AND Low Tire Pressure).
* **IoT Integration:** Connecting the system to an OBD-II scanner for real-time data streaming from a physical car.

---

## 👥 Project Team

* **Vedant Nindrajog**
* **Satya Prakash**