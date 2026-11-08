def mean_price(prices: list[float]) -> float:
    if not prices:
        return 0.0
    return sum(prices) / len(prices)
