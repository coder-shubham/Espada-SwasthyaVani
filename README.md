# Espada-SwasthyaVani – AI-Powered Healthcare Assistant

**SwasthyaVani** is an AI-driven, multilingual IVR and SMS-based healthcare assistant designed to empower rural and underserved populations. It bridges critical gaps in healthcare accessibility, affordability, and health literacy—particularly for communities without smartphones, stable internet, or technical fluency.

🌐 [Live Demo (MVP)](https://swasthyavani.online/)

---

## 🧠 Problem Statement

Rural India continues to struggle with:
- Limited access to primary healthcare and government schemes
- Poor awareness and communication during teleconsultations
- Confusing prescriptions with no local-language explanation
- Technology, literacy, and internet barriers

---

## ✅ Unique Selling Propositions (USP)

1. 📞 **IVR & SMS-based Access** – Works on feature phones; no app or internet required.  
2. 🗣️ **Multilingual AI Voice Support** – Understands and speaks Indian regional languages.  
3. 🚦 **AI-Powered Triage** – Classifies patient needs (Green/Yellow/Red) and provides guided steps.  
4. 📜 **Personalized Scheme Guidance** – Detects eligibility and explains relevant government health schemes.  
5. 💊 **Prescription Explanation** – Describes medicines, timing, and dosages in the user’s local language.  
6. 💻 **Open Source + Cloud-first** – Built on scalable, cost-effective infrastructure and models.

---

## 🛠️ Technology Stack

### 🔹 Backend
- **Java 17+**, **SpringBoot**, **Gradle 8+**  
  REST APIs and Webhook listeners for handling SMS/IVR events, managing session state, and Kafka-based communication.

### 🔹 AI Services
- **Python 3.12+**  
  For handling LLM interactions, STT (speech-to-text), TTS (text-to-speech), and vector DB queries.

### 🔹 Streaming & Messaging
- **Apache Kafka**  
  Facilitates asynchronous communication between backend and AI modules. Ensures scalability and decoupled processing.

### 🔹 UI (Demo)
- **React + Vite**, **JavaScript**, **HTML/CSS**  
  Demo frontend to simulate interactions and show conversation flow.

---

## 🤖 AI & Open Source Models Used

| Purpose                  | Model                        |
|--------------------------|------------------------------|
| Understanding Query      | `LLaMA 3.3 70B`               |
| Contextualization        | `LLaMA 3.1 405B`              |
| Speech to Text (STT)     | `Whisper Large V3`           |
| Text to Speech (TTS)     | `IndicTTS` (Indian languages)|
| Vector Search            | `Weaviate`                   |

---

## Architecture Diagram

![image](https://github.com/user-attachments/assets/7465b573-b024-4dad-a343-85c208fd4d0d)

## UseCase Diagram

![image](https://github.com/user-attachments/assets/a030cd71-e926-4d3c-8255-74972a4cccfa)


## 📁 Project Structure

```
repo/
├── ai/                   # Python AI microservice
│   └── app.py, models/, utils/, ...
├── backend/
│   └── swasthyavani/     # Java SpringBoot backend
│       └── src/, config/, ...
├── ui/                   # React-based demo frontend
│   └── index.html, App.jsx, ...
├── kafka/                # Docker setup for Kafka
│   └── docker-compose.yml
└── README.md             # Project overview
```

---

## 🚀 Getting Started – Local Setup

### 📱 UI (Frontend Demo)

```bash
cd ui/
npm install
npm run build
npm run dev
```
- Runs at: `http://localhost:5173`

---

### 🔄 Kafka (Messaging)

```bash
cd kafka/
docker-compose pull
docker-compose up -d
```
- Kafka Broker: `localhost:9092`

---

### 🧩 Backend (Java SpringBoot)

```bash
cd backend/swasthyavani/
./gradlew bootrun -x test
```
- Backend Server: `http://localhost:8090`

---

### 🧠 AI Microservice (Python)

```bash
cd ai/
pip install -r requirements.txt
python3 app.py
```

---

## 🔮 Future Enhancements

1. 🤖 Make the solution agentic to dynamically guide users through the journey.
2. 🔗 Integrate with eSanjeevani for streamlined consultations.
3. 📱 Launch a lightweight mobile app with support for alarms, profiles, reminders.
4. 📊 Add analytics for government health policy planners and NGOs.
5. 🔄 Improve continuous learning from user feedback using fine-tuned models.

---

## 📈 Scalability Considerations

1. ☁️ Move entire solution to cloud-native infrastructure for horizontal scaling.
2. 🧩 Design modular microservices for separation of concerns and easy upgrades.
3. 🌐 Add support for more Indian languages via IndicNLP and Bhashini integration.
4. 📦 Use containerization (Docker) and orchestration (K8s) for deployments.
5. 📊 Scale Vector DB (Weaviate) for millions of context entries per use case.
