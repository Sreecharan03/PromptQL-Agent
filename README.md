# 🧠 PromptQL-Agent

**Conversational SQL Assistant powered by LangGraph, Azure OpenAI, and Streamlit**

PromptQL-Agent is an agentic AI system that transforms natural language queries into SQL, executes them on your database, and returns both tabular and visual insights — all inside a Streamlit interface.

---

## 🚀 Key Features

- 🧩 **LangGraph Agent Flow** for modular, explainable NLP-to-SQL pipelines
- 💬 **Natural Language → SQL** via Azure OpenAI GPT-4o
- 🧠 **Schema-aware reasoning** using Azure Cognitive Search or Weaviate
- 📊 **Auto-generated Charts** with Plotly (bar, pie, timeline, etc.)
- 🧾 **Summarizer Agent** for human-readable data interpretations
- 🌐 **Multilingual support** (English, Hindi, Telugu)
- 🛡️ **Safe SQL mode** with injection protection and fallback handling

---

## 🧱 Project Structure

```
PromptQL-Agent/
├── agents/
│   ├── sql_generator_agent.py
│   ├── schema_retriever_agent.py
│   ├── visualizer_agent.py
│   └── summarizer_agent.py
├── core/
│   ├── sql_executor.py
│   ├── config.py
│   └── db_connector.py
├── ui/
│   └── app.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔄 Agentic Flow (LangGraph)

```
[Chat Input]
    ↓
[Intention Classifier Agent]
    ↓
[SQL Generator Agent] ← Schema Retriever Agent
    ↓
[SQL Executor Agent]
    ↓
[Plot Generator Agent] → [Summarizer Agent]
    ↓
[Streamlit Display]
```

---

## 🔧 Setup Instructions

```bash
git clone https://github.com/Sreecharan03/PromptQL-Agent.git
cd PromptQL-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Add your keys and DB URI to .env
cp .env.example .env
```

---

## ▶️ Run the App

```bash
streamlit run ui/app.py
```

---

## 📁 .env Configuration (Example)

```env
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
SQL_DATABASE_URL=postgresql://user:pass@host:port/dbname
COGNITIVE_SEARCH_KEY=your_search_key
COGNITIVE_SEARCH_ENDPOINT=https://your-search-endpoint
```

---

## 🛠️ Tech Stack

| Component       | Tech                          |
|----------------|-------------------------------|
| LLM             | Azure OpenAI GPT-4o           |
| Agent Framework | LangGraph                     |
| UI              | Streamlit                     |
| Visuals         | Plotly                        |
| DB Support      | PostgreSQL, MySQL, MSSQL      |
| Retrieval       | Azure Cognitive Search / Weaviate |

---

## ✅ TODO / Coming Soon

- Voice-based query input (Hindi, Telugu)
- Live database schema viewer
- Save queries as report templates
- Grafana dashboard integration

---

## 👨‍💻 Author

Built with ❤️ by [@Sreecharan03](https://github.com/Sreecharan03) — AI, Agents, and Analytics Enthusiast.

---

## 🪪 License

This project is licensed under the MIT License.
