## Ai Knowledge Studio(langchain RAG Application)


A RAG-based document analysis backend built with **FastAPI**, **LangChain**, **Groq**, and **ChromaDB**. Upload documents and generate summaries, quizzes, flashcards, mindmaps, concept breakdowns, roadmaps, and more — powered by a multi-LLM chain pipeline.

## Features

- **Document ingestion**: PDF, DOCX, TXT, and URL support
- **RAG pipeline**: History-aware retrieval with ChromaDB vector store
- **Multi-feature chains**: summary, concepts, questions, mindmap, quiz, flashcards, counterarguments, missing-knowledge analysis, learning roadmaps, and explain-simple/technical modes
- **4-LLM merge pipeline**: base analysis → parallel refinement (2 LLMs) → final merge (1 LLM) for higher-quality outputs
- **Conversational chat**: session-based chat history with MongoDB-backed memory
- **Universal fallback**: graceful handling when no relevant document context is found

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| LLM Orchestration | LangChain (LCEL, `RunnableWithMessageHistory`) |
| LLM Provider | Groq (`ChatGroq`) |
| Vector Store | ChromaDB |
| Embeddings | HuggingFace |
| Metadata / Memory | MongoDB |
| Deployment | Railway |

## Project Structure

```
.
├── main.py                      # FastAPI app entrypoint
├── config.py                    # LLM instances (llm_1..llm_4), env config
├── chains/
│   └── feautres_chain.py        # Core chain orchestration, run_chain(), 4-LLM merge
├── database/
│   └── vector_store.py          # ChromaDB retriever setup
├── memory/
│   └── conversation_memory.py   # Session-based chat history (MongoDB)
├── prompts/
│   ├── summary_prompt.py
│   ├── concept_prompt.py
│   ├── questions_prompt.py
│   ├── mindmap_prompt.py
│   ├── quiz_prompt.py
│   ├── flashcard_prompt.py
│   ├── counterargs_prompt.py
│   ├── explainsimple_prompt.py
│   ├── explaintechnical_prompt.py
│   ├── missingKnowledge_prompt.py
│   ├── roadmap_prompt.py
│   ├── chat_prompt.py
│   └── fallback_prompt.py
├── requirements.txt
└── .env                        
```

## Environment Variables

Create a `.env` file locally (and set these in your deployment platform's dashboard — **`.env` is never deployed**):

```env
GROQ_API_KEY=your_groq_api_key_here
LLM_TEMPERATURE=0.3
```



## Setup (Local Development)

```bash
# clone and enter the project
git clone <your-repo-url>
cd <project-folder>

# create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# add your .env file with GROQ_API_KEY

# run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Deployment (Railway)

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```





## Core Chain Architecture

`run_chain()` in `chains/feautres_chain.py` handles all feature requests:

1. Retrieves conversation history (if `sessionId` provided).
2. Runs a history-aware retriever against ChromaDB to fetch relevant document context.
3. If context is found, feeds it through the requested feature's prompt/parser pair (`CHAIN_MAP`).
4. Optionally routes through the **4-LLM merge pipeline**:
   - `llm_1` → base pass using the feature's prompt
   - `llm_2` + `llm_3` → parallel refinement (concurrent)
   - `llm_4` → merges both refinements into the final structured output
5. If no context is found, falls back to type-appropriate empty/default responses or the universal fallback chain.


## Frontend Integration

The frontend (Vite + React) expects the backend URL in its build-time environment variable:

```env
VITE_BACKEND_URL= you backendUrl or localhost backendUrl
```


