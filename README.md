# ✨ Aura Skincare Voice Agent

Aura is an AI-powered skincare assistant that provides skincare guidance, product recommendations, product details, and basic order support through a simple voice-enabled web interface.

## 🚀 Features

- 🎙️ Voice input using the browser microphone
- 🔊 Voice responses using browser speech synthesis
- 🌿 Skin-type based product recommendations
- 🔎 Product search by category
- 🧴 Detailed product information
- 💰 Product price and category information
- 📦 Order status and tracking
- ❌ Order cancellation eligibility
- 🔄 Return information
- 🚚 Shipping information
- 💬 Interactive chat interface
- ⚡ FastAPI backend
- 🌐 HTML, CSS and JavaScript frontend
- 🗃️ JSON-based product and order data

## 🛠️ Technology Stack

### Frontend
- HTML
- CSS
- JavaScript
- Web Speech API

### Backend
- Python
- FastAPI
- Uvicorn

### Data
- JSON

## 📁 Project Structure

```text
aura-voice-agent/
│
├── backend/
│   ├── data/
│   │   ├── orders.json
│   │   └── products.json
│   ├── main.py
│   └── order_tools.py
│
├── frontend/
│   ├── index.html
│   └── script.js
│
├── README.md
└── .env