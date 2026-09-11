"""Deterministic scoring guardrail for the LLM-generated investment memo.

The language model explains the evidence, but this module keeps the core
recommendation reproducible and auditable from the numeric inputs.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, value)), 2)


def _number(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _sentiment_average(news: Iterable[Dict[str, Any]]) -> float | None:
    scores = []
    for article in news:
        score = _number(article.get("sentiment_score"))
        if score is not None:
            scores.append(max(-1.0, min(1.0, score)))
    return sum(scores) / len(scores) if scores else None


def calculate_recommendation_score(
    ratios: Dict[str, Any] | None = None,
    technical_signals: Dict[str, Any] | None = None,
    news: Iterable[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Return a reproducible 0-100 score with component-level explanations.

    Missing data is excluded from the weighted average rather than silently
    treated as a positive or negative signal.
    """

    ratios = ratios or {}
    technical_signals = technical_signals or {}
    components: Dict[str, float] = {}
    explanations: Dict[str, str] = {}

    pe = _number(ratios.get("pe"))
    pb = _number(ratios.get("pb"))
    roe = _number(ratios.get("roe"))
    debt_to_equity = _number(ratios.get("debt_to_equity"))
    fundamental_points = []
    if pe is not None and pe > 0:
        fundamental_points.append(80 if pe <= 12 else 65 if pe <= 20 else 45 if pe <= 35 else 25)
    if pb is not None and pb > 0:
        fundamental_points.append(75 if pb <= 1.5 else 60 if pb <= 3 else 40 if pb <= 6 else 25)
    if roe is not None:
        fundamental_points.append(85 if roe >= 20 else 70 if roe >= 15 else 55 if roe >= 10 else 30)
    if debt_to_equity is not None:
        fundamental_points.append(80 if debt_to_equity <= 80 else 65 if debt_to_equity <= 150 else 45 if debt_to_equity <= 250 else 25)
    if fundamental_points:
        components["fundamental"] = round(sum(fundamental_points) / len(fundamental_points), 2)
        explanations["fundamental"] = f"Scored {len(fundamental_points)} valuation, profitability and leverage inputs."

    trend = str(technical_signals.get("trend_summary", "")).lower()
    technical_points = []
    if "bullish" in trend:
        technical_points.append(75)
    elif "bearish" in trend:
        technical_points.append(25)
    elif trend:
        technical_points.append(50)
    rsi = _number(technical_signals.get("rsi"))
    if rsi is not None:
        technical_points.append(65 if 45 <= rsi <= 65 else 75 if rsi < 30 else 35 if rsi > 70 else 50)
    macd = _number(technical_signals.get("macd_line"))
    signal = _number(technical_signals.get("macd_sig"))
    if macd is not None and signal is not None:
        technical_points.append(70 if macd > signal else 30)
    if technical_points:
        components["technical"] = round(sum(technical_points) / len(technical_points), 2)
        explanations["technical"] = f"Scored {len(technical_points)} trend and momentum signals."

    average_sentiment = _sentiment_average(news or [])
    if average_sentiment is not None:
        components["sentiment"] = round((average_sentiment + 1.0) * 50.0, 2)
        explanations["sentiment"] = f"Average news sentiment is {average_sentiment:.2f} on a -1 to 1 scale."

    weights = {"fundamental": 0.45, "technical": 0.35, "sentiment": 0.20}
    active_weight = sum(weights[name] for name in components)
    total = sum(components[name] * weights[name] for name in components) / active_weight if active_weight else 50.0
    total = _clamp(total)
    recommendation = "BUY" if total >= 65 else "SELL" if total < 40 else "HOLD"

    return {
        "score": total,
        "recommendation": recommendation,
        "components": components,
        "weights": {name: weights[name] for name in components},
        "average_sentiment": round(average_sentiment, 4) if average_sentiment is not None else None,
        "explanations": explanations,
        "data_coverage": round(active_weight, 2),
    }
