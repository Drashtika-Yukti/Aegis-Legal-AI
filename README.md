# ⚖️ Aegis Legal AI v2.0
![Aegis CI Pipeline](https://github.com/Drashtika-Yukti/LexiGuard-AI-Engine/actions/workflows/ci.yml/badge.svg)
![Aegis CD Pipeline](https://github.com/Drashtika-Yukti/LexiGuard-AI-Engine/actions/workflows/cd.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Aegis Legal AI** is a premium, enterprise-grade Legal Intelligence platform. It leverages **Agentic RAG** and **Multi-Agent Orchestration** to provide high-fidelity legal reasoning while strictly enforcing data privacy through local PII masking.

---

## 🏛️ Enterprise Architecture
The project is structured as a robust monorepo for maximum scalability and professional integration:

- **`engine/`**: The core AI intelligence (FastAPI + LangGraph + Groq).
- **`studio/`**: Premium legal workspace (React + Vite + Axios).
- **`workers/`**: Specialized high-performance microservices (Golang Ingestor).
- **`evals/`**: Trust & Evaluation layer (RAGAS + DeepEval).
- **`deploy/`**: Infrastructure and orchestration (Docker + K8s).

---

## 🚀 Key Features
*   **Agentic RAG**: Self-grading retrieval system with hallucination detection.
*   **Privacy Guard**: Local NER-based PII masking via spaCy before cloud transmission.
*   **Aegis Studio**: A solid, professional UI designed for high-trust legal environments.
*   **Automated Trust**: Integrated RAGAS and DeepEval metrics for legal integrity.
*   **High Speed**: Legal ingestion powered by a high-performance Go worker.

---

## ⚙️ Deployment
```powershell
docker-compose up --build
```
- **Aegis Studio**: http://localhost:5173
- **Aegis Engine API**: http://localhost:8000/docs

---

## 🛡️ Trust & Evaluation
Aegis includes a dedicated `evals/` ecosystem to ensure legal accuracy:
*   **RAGAS**: Faithfulness & Context Precision.
*   **DeepEval**: Assertive legal unit testing.
*   **LangSmith**: Complete observability and decision tracing.

---

## 📜 License
This project is for professional enterprise use and adheres to strict data privacy standards. MIT Licensed.
