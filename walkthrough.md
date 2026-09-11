# MarketCortex walkthrough

## Delivered

- Added deterministic recommendation scoring in `src/domain/services/recommendation_scoring.py`.
- Added an LLM-independent MA20/MA50 + RSI14 backtest engine in `src/domain/services/backtesting.py`.
- Added `GET /api/v1/backtest` and exposed score/breakdown fields in the analysis response.
- Added score coverage display to the browser UI.
- Added unit tests, pytest configuration, CI workflow and a project-focused README.
- Renamed the project branding, API metadata, UI labels and default database to MarketCortex.
- Published MarketCortex to `chungnguyenvp/Pj` from a clean root commit owned solely by `chungnguyenvp`.

## Verification

- `python -m compileall -q src tests`: passed after the MarketCortex rename.
- Legacy-brand scan across product source and documentation: passed with no remaining previous-name references.
- The bundled local Python runtime does not include `pytest`; GitHub Actions installed the complete dependency set and passed the unit-test workflow on both `main` and `feat/finsight-v1`.

## Design note

The LLM remains responsible for natural-language synthesis, while the numeric score and backtest are deterministic. This separation makes the recommendation easier to audit and the evaluation reproducible.
