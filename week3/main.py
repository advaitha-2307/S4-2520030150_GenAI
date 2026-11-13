import os
from dotenv import load_dotenv

from mongo_logger import MongoLogger
from llm_client import GeminiProvider, OllamaProvider, LLMClient

load_dotenv()

def main():
    print("=== LLM Monitoring System ===")

    # Select provider
    choice = input("Choose provider (1 = Gemini, 2 = Ollama): ")

    if choice == "1":
        provider = GeminiProvider()
    elif choice == "2":
        provider = OllamaProvider()
    else:
        print("Invalid choice!")
        return

    # Connect MongoDB
    logger = MongoLogger()

    # Create LLM client
    llm = LLMClient(provider, logger)

    try:
        prompt = input("\nEnter your prompt: ")
        llm.generate(prompt)
    finally:
        logger.close()


if __name__ == "__main__":
    main()