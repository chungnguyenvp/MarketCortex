# MarketCortex

Explainable multi-agent stock research and backtesting for Vietnamese and US equities.

MarketCortex combines deterministic financial calculations with LangGraph specialist agents. The system gathers market data, financial ratios, news and optional annual-report PDFs, then produces an evidence-aware research memo and a reproducible quantitative recommendation score. It is a research aid, not financial advice or an automated trading system.

## Why this project is different

- **Multi-agent research workflow**: routing, fundamental, technical, sentiment, CIO synthesis and an auditor/reflection loop.
- **Quantitative guardrail**: a deterministic 0–100 score combines valuation, profitability, leverage, momentum and news sentiment. The LLM explains the score instead of inventing numeric inputs.
- **PDF RAG**: LlamaParse Markdown extraction (with local `pypdf` fallback) and persistent ChromaDB retrieval for financial reports.
- **Backtesting API**: a reproducible MA20/MA50 + RSI14 strategy reports return, volatility, Sharpe ratio, maximum drawdown and benchmark performance.
- **Operational controls**: SQLite caching, persisted LangGraph checkpoints, input validation, structured logs and unit tests.

## Architecture

```text
Browser (HTML/CSS/JS + Plotly)
        |
        v
FastAPI REST API -----> SQLite cache/history
        |
        v
LangGraph orchestrator
  |       |        |
  v       v        v
Fund.  Technical  Sentiment
  \       |        /
   \      v       /
      CIO synthesis ---> Critic ---> targeted revision (max 2)
              |
              v
        Markdown report + score
```

## Main endpoints

```text
GET  /health
POST /api/v1/analyze
GET  /api/v1/backtest?ticker=FPT&market=VN&days=730
GET  /api/v1/history
GET  /api/v1/history/{id}
DELETE /api/v1/history/{id}
```

## Run locally

Requires Python 3.10+.

```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Set at least one Gemini credential in `.env`:

```env
GEMINI_API_KEY=your_key
DATABASE_URL=data/marketcortex.db
CHROMA_DB_PATH=data/chroma_store
```

Open `http://localhost:8000` for the UI and `http://localhost:8000/docs` for Swagger.

Run tests with:

```bash
python -m pytest tests/ -q
```

## Data and fallback behavior

- VN price/ratio data uses `vnstock`; US data uses `yfinance`.
- VN news uses CafeF scraping; US news uses the `yfinance` feed.
- FinBERT is used when its model is available; a small Vietnamese keyword scorer is used as an offline fallback.
- If a news scraper fails, demo fallback articles may be generated. They are marked as mock data and must not be used for real investment decisions.

## Project layout

```text
src/agents/                  LangGraph nodes and prompts
src/api/                     FastAPI routes and Pydantic schemas
src/domain/services/         Calculations, scoring, validation, backtesting
src/infrastructure/adapters/ vnstock, yfinance, Gemini, FinBERT, RAG, scraping
src/infrastructure/database/ SQLite connection, migrations and repositories
static/                      Browser UI
tests/                       Unit and integration tests
```

## Attribution

This repository started from the open-source `financial-analysis-agents` codebase and has been extended for the MarketCortex project with deterministic scoring, the backtesting service/API, UI score presentation, tests and documentation. Please verify the upstream license and retain any required copyright notices before redistributing.

## Disclaimer

This software provides educational research output only. Market data can be delayed, incomplete or unavailable, and AI-generated analysis can be wrong. Always verify sources and consult a qualified adviser before making investment decisions.
