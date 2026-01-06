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

# ============================================================
# FREE MODELS AVAILABLE ON OPENROUTER
# ============================================================
"""
Recommended FREE models (updated Jan 2026):

BEST FOR TAX CALCULATIONS:
- google/gemini-2.0-flash-exp:free        (Fast, accurate, 1M token context)
- google/gemini-flash-1.5:free            (Good balance)
- meta-llama/llama-3.2-3b-instruct:free   (Lightweight)

OTHER FREE OPTIONS:
- qwen/qwen-2-7b-instruct:free
- microsoft/phi-3-mini-128k-instruct:free
- huggingfaceh4/zephyr-7b-beta:free

PAID BUT CHEAP:
- openai/gpt-4o-mini                      ($0.15/1M tokens)
- anthropic/claude-3.5-sonnet             ($3/1M tokens)

Usage: Pass model name to --model flag or set in code
"""

FREE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-flash-1.5:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free"
]

DEFAULT_FREE_MODEL = "google/gemini-2.0-flash-exp:free"

class ResearchLLM:
    def __init__(self, model_name: str = None, api_key: Optional[str] = None):
        """
        Initialize the LLM client with OpenRouter.
        
        Args:
            model_name: Model to use. Defaults to free Gemini 2.0 Flash.
                       See FREE_MODELS list for available free options.
            api_key: OpenRouter API key (optional, reads from env if not provided)
        """
        # Use free model by default
        self.model_name = model_name or DEFAULT_FREE_MODEL
        
        # Get OpenRouter API key
        openrouter_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment!\n"
                "Get a free key at: https://openrouter.ai/keys"
            )
        
        # Initialize OpenAI client with OpenRouter base URL
        self.client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        is_free = ":free" in self.model_name
        logger.info(f"Initialized ResearchLLM with OpenRouter model: {self.model_name} ({'FREE' if is_free else 'PAID'})")

    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Get completion from the model via OpenRouter with retry logic.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (0.0 = deterministic)
            
        Returns:
            Model's response text
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a precise Indian Tax Expert for FY 2024-25."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=1500
                )
                return response.choices[0].message.content.strip()
            except OpenAIError as e:
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} retries failed for model {self.model_name}")
                
        return "ERROR: API Failed after all retries"
