# ⬡ ORCHA — AI Product Feedback Analyst

ORCHA is a multi-agent AI system that automatically researches, analyzes, and summarizes real user feedback for any product using web search and large language models.

## 🧠 How It Works
User enters product name
↓
Planner Agent    → generates search queries
↓
Executor Agent   → searches DuckDuckGo, fetches results
↓
Analyzer Agent   → extracts themes, sentiment, complaints
↓
Summary Agent    → generates executive report
↓
Memory Store     → saves result for future comparison

## ✨ Features

- 🔍 Real-time web search via DuckDuckGo
- 🤖 4 specialized AI agents working together
- 🧠 Persistent memory — never re-analyzes the same product
- ⚖️ Product comparison side by side
- 📄 Export reports as PDF or HTML
- 🌐 Web UI with Analyze, Memory, and Compare tabs
- ⚡ Fast inference via Groq LLaMA 3.1

##  Project Structure
ORCHA/
├── api/
│   ├── main.py           # FastAPI app
│   └── routes.py         # API endpoints
├── agents/
│   ├── planner_agent.py  # generates search plan
│   ├── executor_agent.py # runs searches
│   ├── analyzer_agent.py # extracts insights
│   └── summary_agent.py  # generates final report
├── tools/
│   ├── llm.py            # Groq LLM client
│   └── search.py         # DuckDuckGo search tool
├── orcha_memory/
│   └── memory_store.py   # save/retrieve/compare analyses
├── reports/
│   └── report.py         # PDF and HTML export
├── frontend/
│   ├── index.html        # main UI
│   ├── style.css         # styling
│   └── app.js            # frontend logic
├── config.py             # settings and environment
├── main.py               # CLI interface
└── README.md             # project documentation

## 🚀 Live Demo
- Live URL: http://54.89.20.133:8000