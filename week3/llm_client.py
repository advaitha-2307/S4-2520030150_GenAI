import os
import time
import requests
from google import genai

from cost_calculator import calculate_cost


class GeminiProvider:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.model = "gemini-3.8-flash"

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        usage = response.usage_metadata

        input_tokens = usage.prompt_token_count or 0
        output_tokens = usage.candidates_token_count or 0

        return {
            "text": response.text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }


class OllamaProvider:
    def __init__(self):
        self.model = "llama3.2"
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt):
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        return {
            "text": data["response"],
            "input_tokens": data.get("prompt_eval_count", 0),
            "output_tokens": data.get("eval_count", 0)
        }


class LLMClient:
    def __init__(self, provider, mongo_logger):
        self.provider = provider
        self.mongo_logger = mongo_logger

    def generate(self, prompt):
        start_time = time.perf_counter()

        try:
            result = self.provider.generate(prompt)

            latency = round(
                time.perf_counter() - start_time, 3
            )

            model = self.provider.model

            cost = calculate_cost(
                model,
                result["input_tokens"],
                result["output_tokens"]
            )

            log_data = {
                "provider": self.provider.__class__.__name__,
                "model": model,
                "prompt": prompt,
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "total_tokens": (
                    result["input_tokens"] +
                    result["output_tokens"]
                ),
                "latency_seconds": latency,
                "estimated_cost_usd": cost,
                "attempts": 1,
                "status": "success",
                "error": None
            }

            self.mongo_logger.log_call(log_data)

            print("\nResponse:", result["text"])
            print("Latency:", latency, "seconds")
            print("Input tokens:", result["input_tokens"])
            print("Output tokens:", result["output_tokens"])
            print("Estimated cost (USD):", cost)

            return result["text"]

        except Exception as error:
            latency = round(
                time.perf_counter() - start_time, 3
            )

            self.mongo_logger.log_call({
                "provider": self.provider.__class__.__name__,
                "model": self.provider.model,
                "prompt": prompt,
                "latency_seconds": latency,
                "attempts": 1,
                "status": "failed",
                "error": str(error)
            })

            print("LLM call failed:", error)
            return None