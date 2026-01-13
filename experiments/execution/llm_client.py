import os
import time
import logging
from typing import Optional

# Configure logger
logger = logging.getLogger("experiments.llm")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - LLM - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

class ResearchLLM:
    def __init__(self, model_name: str = None, api_key: Optional[str] = None):
        """
        Initialize the LLM client with support for:
        - OpenAI (gpt-* models)
        - OpenRouter (other models via :free suffix)
        - Google AI Studio (gemini-* models with GOOGLE_API_KEY)
        - Google Vertex AI (gemini-* or vertex/* models with GOOGLE_CLOUD_PROJECT)
        
        Auto-detects API based on model name pattern and available credentials.
        """
        self.model_name = model_name or "google/gemini-2.0-flash-exp:free"
        
        # Determine which API to use
        is_gemini_model = (
            self.model_name.startswith("gemini-") or 
            self.model_name.startswith("vertex/") or
            (self.model_name.startswith("google/gemini-") and ":free" not in self.model_name)
        )
        
        # Prefer Google AI Studio if API key is available (simpler than Vertex AI)
        self.use_google_ai_studio = (
            is_gemini_model and 
            os.environ.get("GOOGLE_API_KEY") is not None
        )
        
        self.use_vertex_ai = (
            is_gemini_model and 
            not self.use_google_ai_studio and
            os.environ.get("GOOGLE_CLOUD_PROJECT") is not None
        )
        
        self.use_openai_direct = (
            self.model_name.startswith("gpt-") or 
            self.model_name.startswith("openai/gpt")
        )
        
        if self.use_google_ai_studio:
            self._init_google_ai_studio()
        elif self.use_vertex_ai:
            self._init_vertex_ai()
        elif self.use_openai_direct:
            self._init_openai()
        else:
            self._init_openrouter()
    
    def _init_google_ai_studio(self):
        """Initialize Google AI Studio client (simpler Gemini API)"""
        try:
            import google.generativeai as genai
            
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY not found in environment!\n"
                    "Get a key at: https://aistudio.google.com/app/apikey"
                )
            
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Map model name to Google AI Studio format
            if self.model_name.startswith("vertex/"):
                studio_model = self.model_name.replace("vertex/", "")
            elif self.model_name.startswith("google/gemini-"):
                studio_model = self.model_name.replace("google/", "")
            else:
                studio_model = self.model_name
            
            # Map common model names to actual available models
            model_mappings = {
                "gemini": "gemini-2.0-flash",
                "gemini-flash": "gemini-2.0-flash",
                "gemini-1.5-flash": "gemini-2.0-flash",  # Map old name to new
                "gemini-pro": "gemini-2.0-flash",
                "gemini-1.5-pro": "gemini-2.5-pro",  # Map old pro to new
            }
            
            studio_model = model_mappings.get(studio_model, studio_model)
            
            # Add 'models/' prefix if not present (required by API)
            if not studio_model.startswith("models/"):
                studio_model = f"models/{studio_model}"
            
            self.client = genai.GenerativeModel(studio_model)
            self.api_type = "google_ai_studio"
            logger.info(f"✅ Initialized with Google AI Studio: {studio_model}")
            
        except ImportError:
            raise ValueError(
                "Google Generative AI library not installed!\n"
                "Install: pip install google-generativeai"
            )
    
    def _init_vertex_ai(self):
        """Initialize Google Vertex AI client"""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            # Get project ID from environment or gcloud config
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                try:
                    import subprocess
                    result = subprocess.run(
                        ["gcloud", "config", "get-value", "project"],
                        capture_output=True, text=True, check=True
                    )
                    project_id = result.stdout.strip()
                except:
                    raise ValueError(
                        "GOOGLE_CLOUD_PROJECT not set and gcloud config not found!\n"
                        "Set project: export GOOGLE_CLOUD_PROJECT=your-project-id"
                    )
            
            location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            
            # Map model name
            if self.model_name.startswith("vertex/"):
                vertex_model = self.model_name.replace("vertex/", "")
            elif self.model_name.startswith("google/gemini-"):
                vertex_model = self.model_name.replace("google/", "")
            else:
                vertex_model = self.model_name
            
            # Default to gemini-1.5-flash if just "gemini" specified
            if vertex_model == "gemini":
                vertex_model = "gemini-1.5-flash"
            
            self.client = GenerativeModel(vertex_model)
            self.api_type = "vertex_ai"
            logger.info(f"✅ Initialized with Google Vertex AI: {vertex_model} (Project: {project_id})")
            
        except ImportError:
            raise ValueError(
                "Google Cloud AI Platform library not installed!\n"
                "Install: pip install google-cloud-aiplatform"
            )
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        from openai import OpenAI
        
        # Strip "openai/" prefix if present
        if self.model_name.startswith("openai/"):
            self.model_name = self.model_name.replace("openai/", "")
        
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment!\n"
                "Get a key at: https://platform.openai.com/api-keys"
            )
        
        self.client = OpenAI(api_key=openai_key)
        self.api_type = "openai"
        logger.info(f"✅ Initialized with OpenAI Direct API: {self.model_name}")
    
    def _init_openrouter(self):
        """Initialize OpenRouter client"""
        from openai import OpenAI
        
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment!\n"
                "Get a free key at: https://openrouter.ai/keys"
            )
        
        self.client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.api_type = "openrouter"
        is_free = ":free" in self.model_name
        logger.info(f"✅ Initialized with OpenRouter: {self.model_name} ({'FREE' if is_free else 'PAID'})")

    def predict(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Get completion from the model with retry logic.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (0.0 = deterministic)
            
        Returns:
            Model's response text
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.api_type == "google_ai_studio":
                    return self._predict_google_ai_studio(prompt, temperature)
                elif self.api_type == "vertex_ai":
                    return self._predict_vertex_ai(prompt, temperature)
                else:
                    return self._predict_openai_compatible(prompt, temperature)
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} retries failed for model {self.model_name}")
                
        return "ERROR: API Failed after all retries"
    
    def _predict_google_ai_studio(self, prompt: str, temperature: float) -> str:
        """Google AI Studio prediction"""
        import google.generativeai as genai
        
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=1500,
        )
        
        full_prompt = (
            "You are a precise Indian Tax Expert for FY 2024-25.\n\n"
            f"{prompt}"
        )
        
        response = self.client.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text.strip()
    
    def _predict_vertex_ai(self, prompt: str, temperature: float) -> str:
        """Vertex AI prediction"""
        from vertexai.generative_models import GenerationConfig
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=1500,
        )
        
        full_prompt = (
            "You are a precise Indian Tax Expert for FY 2024-25.\n\n"
            f"{prompt}"
        )
        
        response = self.client.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text.strip()
    
    def _predict_openai_compatible(self, prompt: str, temperature: float) -> str:
        """OpenAI-compatible API prediction (OpenAI, OpenRouter)"""
        from openai import OpenAIError
        
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
