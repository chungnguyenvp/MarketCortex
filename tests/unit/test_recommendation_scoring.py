from src.domain.services.recommendation_scoring import calculate_recommendation_score


def test_score_is_deterministic_and_buy_for_strong_inputs():
    result = calculate_recommendation_score(
        {"pe": 10, "pb": 1.2, "roe": 22, "debt_to_equity": 40},
        {"trend_summary": "Bullish", "rsi": 55, "macd_line": 2, "macd_sig": 1},
        [{"sentiment_score": 0.8}, {"sentiment_score": 0.4}],
    )
    assert result["recommendation"] == "BUY"
    assert result["score"] > 65
    assert set(result["components"]) == {"fundamental", "technical", "sentiment"}


def test_missing_inputs_are_not_treated_as_positive_signals():
    result = calculate_recommendation_score({}, {}, [])
    assert result["score"] == 50.0
    assert result["data_coverage"] == 0.0
    assert result["components"] == {}
