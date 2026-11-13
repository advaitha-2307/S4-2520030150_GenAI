# Sample pricing per 1 million tokens (USD)
MODEL_PRICING = {
    "gemini-3.8-flash": {
        "input": 0.50,
        "output": 2.00
    }
}


def calculate_cost(model, input_tokens, output_tokens):
    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return None

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return round(input_cost + output_cost, 8)