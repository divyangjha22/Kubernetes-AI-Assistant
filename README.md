# Kubernetes-AI-Assistant

Architecture
user -> Streamlit UI -> Fast API -> NeMo Guardrails -> Agent -> LangGraph Memory Saver

Components
1. UI
2. API + Safety Gate
3. Agent Engine
4. Knowledge & LLMs
5. Data Ingestion
6. Evaluation - RAGAS
7. Monitoring & Observability

Data Ingestion Pipeline
Raw Data -> Smart Parser -> PDF/HTML/Text/Docx/PPT -> Semantic Chunker -> Embeddings -> Qdrant Cloud