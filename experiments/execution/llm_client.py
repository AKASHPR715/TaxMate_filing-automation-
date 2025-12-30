import os
import time
import logging
from typing import Optional
from openai import OpenAI, OpenAIError

# Configure logger
logger = logging.getLogger("experiments.llm")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - LLM - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

class ResearchLLM:
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize the LLM client.
        Default to gpt-4o-mini for cost-effectiveness.
        """
        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            # Ensure base_url IS NOT set to local unless explicitly requested
        )
        logger.info(f"Initialized ResearchLLM with model: {self.model_name}")

    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Get completion from the model with retry logic.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a precise Indian Tax Expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except OpenAIError as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
        logger.error("All retries failed.")
        return "ERROR: API Failed"
