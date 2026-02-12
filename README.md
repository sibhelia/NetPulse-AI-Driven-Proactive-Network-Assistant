# NetPulse - AI-Driven Proactive Network Assistant

NetPulse is an advanced Network Operations Center (NOC) dashboard designed to proactively monitor, analyze, and predict network faults using Artificial Intelligence. By leveraging hybrid machine learning models (LSTM + Random Forest), NetPulse moves beyond traditional reactive monitoring to predictive maintenance, identifying potential issues before they impact the customer experience.

## key Features

### 1. AI-Powered Predictive Analysis
*   **Hybrid Model Architecture:** Combines Random Forest for real-time snapshot classification with LSTM (Long Short-Term Memory) deep learning for time-series trend analysis.
*   **Trend Detection:** Capable of forecasting network degradation up to 30 minutes in advance.
*   **Smart Classification:** Categorizes subscribers into Green (Healthy), Yellow (At Risk/Degrading), and Red (Critical Fault) statuses based on live telemetry.

### 2. Real-Time Dashboard & Visualization
*   **Interactive Regional Map:** Visualizes network health across different geographical districts using color-coded indicators.
*   **Live Status Tracking:** Real-time updates of subscriber connectivity status, latency, packet loss, and SNR margins.
*   **Data-Driven Insights:** Comprehensive charts and graphs (Pie charts, Bar charts) displaying fault distribution and technician performance.

### 3. Automated Incident Management
*   **Auto-Ticketing:** Automatically generates support tickets when a critical fault (Red) or degradation trend (Yellow) is detected.
*   **Intelligent Routing:** Assigns tickets to the appropriate technician based on fault type (e.g., Fiber, DSL) and availability.
*   **LLM Integration:** Uses Google Gemini AI to analyze raw technical logs and generate human-readable "Technician Notes" for faster troubleshooting.

### 4. Field Operations Integration
*   **Telegram Notifications:** Instantly notifies field technicians via Telegram when a new ticket is assigned or a high-priority fault occurs.
*   **Job Management:** Technicians can view task details, subscriber location, and suggested solutions directly from the notification system.

### 5. Simulation & Testing
*   **Robust Data Simulation:** Includes a robust simulation engine (`seed_db.py`) to generate realistic network traffic patterns, fault scenarios, and subscriber behaviors for demonstration and testing purposes.

---

## Technical Stack

### Backend
*   **Framework:** Python FastAPI (High-performance, async execution)
*   **Database:** PostgreSQL (Relational data storage for subscribers, tickets, and logs)
*   **AI/ML:**
    *   **TensorFlow/Keras:** LSTM models for time-series forecasting.
    *   **Scikit-learn:** Random Forest classifiers and data preprocessing.
    *   **Google Gemini AI:** Generative AI for log analysis and summarization.
*   **Utilities:** Pandas, NumPy, Joblib, Psycopg2.

### Frontend
*   **Framework:** React.js (Vite)
*   **Visualization:** Recharts (Data charts), Leaflet (Interactive maps).
*   **Styling:** Modern CSS3 with responsive design principles.
*   **State Management:** React Hooks and Context API.

---

## Installation & Setup

### Prerequisites
*   Python 3.11 or higher
*   Node.js & npm
*   PostgreSQL Database

### 1. Database Setup
Create a PostgreSQL database named `netpulse_db`.
Update the database connection settings in `src/backend/.env` (or directly in configuration files if applicable).

### 2. Backend Installation
Navigate to the backend directory:
```bash
cd NetPulse-AI-Driven-Proactive-Network-Assistant/src/backend
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

Initialize the database schema and seed simulation data:
```bash
python init_db_postgres.py
python seed_db.py
```

Start the Backend Server:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The API will be available at `http://localhost:8000`*

### 3. Frontend Installation
Navigate to the frontend directory:
```bash
cd NetPulse-AI-Driven-Proactive-Network-Assistant/src/frontend
```

Install dependencies:
```bash
npm install
```

Start the Frontend Application:
```bash
npm run dev
```
*The application will launch at `http://localhost:5173` (or similar)*

---

## Project Structure

```
NetPulse/
├── src/
│   ├── backend/
│   │   ├── main.py                 # API Entry Point
│   │   ├── lstm_service.py         # AI Model Service (LSTM)
│   │   ├── status_tracker.py       # Logic for detecting status changes
│   │   ├── telegram_service.py     # Telegram Bot Integration
│   │   ├── seed_db.py              # Simulation Data Generator
│   │   └── ...
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── pages/              # Dashboard, Map, List Views
│   │   │   ├── components/         # Reusable UI Components
│   │   │   ├── services/           # API Consumption
│   │   │   └── ...
│   │   └── ...
└── data/                           # Training data and serialized models
```

---

## Contact & Credits
**Developer:** [Sibel Akkurt]
**Project:** NetPulse AI Network Assistant

*NetPulse is a proof-of-concept application demonstrating the power of AI in telecommunications network management.*
