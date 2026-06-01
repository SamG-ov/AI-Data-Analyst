# AI Data Analyst

An AI-powered data analysis platform: upload CSV/Excel files, automatically clean
and explore them, generate charts, ask questions in natural language, and receive
AI-generated business insights and downloadable reports.

## Architecture

| Layer        | Tech                                   | Responsibility                              |
| ------------ | -------------------------------------- | ------------------------------------------- |
| Frontend     | Next.js (React + TypeScript)           | Upload UI, tables, charts, chat, reports    |
| Backend API  | Python + FastAPI                       | Data processing, EDA, LLM orchestration     |
| Data         | pandas, numpy, Plotly                  | Cleaning, analysis, chart generation        |
| AI / LLM     | Anthropic Claude (via official SDK)    | Natural-language Q&A, insights, summaries   |

The frontend never talks to the LLM or touches raw data logic directly — everything
flows through the backend, so API keys stay server-side and the core stays testable.

## Project structure

```
AI-Data-Analyst/
├── backend/     # FastAPI service (Python, managed by uv)
└── frontend/    # Next.js app (added in a later step)
```

## Getting started (backend)

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/).

```bash
cd backend
cp .env.example .env        # then fill in your ANTHROPIC_API_KEY
uv sync                     # create venv + install dependencies
uv run uvicorn app.main:app --reload
```

Then open:
- http://localhost:8000/health — health check
- http://localhost:8000/docs — interactive API docs

Run tests:

```bash
cd backend
uv run pytest
```
