# TikTok Ads AI Agent

An AI-powered agent designed to simulate the creation of TikTok Ad campaigns via a conversational interface. This project demonstrates prompt engineering, guardrails enforcement, and mock API integration.

## 🚀 Features
- **Structured Prompting:** Uses a System Prompt to act as a strict Ad Manager.
- **Guardrails:** Automatically rejects "Conversion" objective ads if no music is provided (Business Rule Enforcement).
- **Mock OAuth:** Simulates token exchange and authentication flow.
- **Resilient Error Handling:** Validates inputs before submission and simulates API responses (200 OK, 400 Bad Request).

## 🛠️ Tech Stack
- Python
- Streamlit (UI)
- LangChain & Groq (LLM: Llama-3.3-70b)

## ⚙️ How to Run
1. Clone the repository.
2. Install dependencies:
   pip install -r requirements.txt
3. Set up your Groq API Key in the sidebar.
4. Run the app:
   streamlit run app.py
