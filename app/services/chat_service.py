"""
TaxMate Chat Service
A generalized chat service for tax advisory using OpenRouter.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# ============================================================
# Logging Setup
# ============================================================
def setup_chat_logger():
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "chat_service.log"
    
    logger = logging.getLogger("chat_service")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fh = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding="utf-8"
        )
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("CHAT: %(message)s"))
        logger.addHandler(ch)
    
    return logger

chat_logger = setup_chat_logger()

# ============================================================
# Configuration
# ============================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model selection - using a capable free model
DEFAULT_MODEL = "kwaipilot/kat-coder-pro:free"

# ============================================================
# System Prompt
# ============================================================
TAXMATE_SYSTEM_PROMPT = """You are **TaxMate**, an expert AI tax advisor specializing in **Indian Income Tax** for **FY 2024-25 (Assessment Year 2025-26)**.

## Your Expertise
- Complete knowledge of the Indian Income Tax Act, 1961
- Expertise in both Old and New Tax Regimes
- Deep understanding of Chapter VI-A deductions (80C, 80D, 80CCD, 80E, 80G, etc.)
- Knowledge of HRA exemptions, LTA, standard deduction rules
- Familiarity with Form 16, Form 26AS, and Annual Information Statement (AIS)
- Understanding of capital gains, rental income, and other income sources

## Tax Regime Comparison (FY 2024-25)

### New Tax Regime (Default)
| Income Range | Tax Rate |
|-------------|----------|
| Up to ₹3,00,000 | Nil |
| ₹3,00,001 - ₹7,00,000 | 5% |
| ₹7,00,001 - ₹10,00,000 | 10% |
| ₹10,00,001 - ₹12,00,000 | 15% |
| ₹12,00,001 - ₹15,00,000 | 20% |
| Above ₹15,00,000 | 30% |

*Standard Deduction: ₹75,000 | Rebate u/s 87A: Up to ₹7,00,000 taxable income*

### Old Tax Regime
| Income Range | Tax Rate |
|-------------|----------|
| Up to ₹2,50,000 | Nil |
| ₹2,50,001 - ₹5,00,000 | 5% |
| ₹5,00,001 - ₹10,00,000 | 20% |
| Above ₹10,00,000 | 30% |

*Standard Deduction: ₹50,000 | Allows Chapter VI-A deductions*

## Key Deductions (Old Regime)
- **Section 80C**: Up to ₹1,50,000 (PPF, ELSS, LIC, EPF, etc.)
- **Section 80CCD(1B)**: Additional ₹50,000 for NPS
- **Section 80D**: Health insurance (₹25,000 self, ₹50,000 senior parents)
- **Section 80E**: Education loan interest (no limit, 8 years)
- **Section 80G**: Donations (50% or 100% deduction)
- **Section 80TTA/80TTB**: Savings interest (₹10,000 / ₹50,000 for seniors)

## Response Guidelines

1. **Be Specific**: Provide exact section numbers, limits, and calculations when applicable
2. **Be Practical**: Give actionable advice the user can implement
3. **Be Clear**: Use simple language, avoid jargon, explain technical terms
4. **Be Structured**: Use bullet points, tables, and clear formatting
5. **Be Honest**: If unsure, acknowledge limitations and recommend consulting a CA

## Context Handling

- **If user data is provided**: Reference their specific income, deductions, and tax situation
- **If no data provided**: Give general guidance and ask clarifying questions
- **Always clarify**: Whether advice is based on their specific data or general rules

## Important Notes
- Tax laws change frequently; recommend verifying with latest notifications
- Complex situations (NRI status, business income, crypto) may need CA consultation
- Always consider both regimes before recommending one
- Due date for FY 2024-25 filing: July 31, 2025 (for non-audit cases)

Remember: You're a helpful, knowledgeable, and friendly tax advisor. Make tax filing less stressful for users! 🇮🇳"""

# ============================================================
# Chat Message Types
# ============================================================
@dataclass
class ChatMessage:
    role: str  # "user" or "assistant" or "system"
    content: str

@dataclass
class ChatSession:
    """Manages a single chat session with history."""
    messages: List[ChatMessage] = field(default_factory=list)
    context: Optional[Dict[str, Any]] = None
    
    def add_user_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="user", content=content))
    
    def add_assistant_message(self, content: str) -> None:
        self.messages.append(ChatMessage(role="assistant", content=content))
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set tax document context for personalized responses."""
        self.context = context
        chat_logger.info(f"Context updated with keys: {list(context.keys()) if context else 'None'}")
    
    def get_context_summary(self) -> str:
        """Generate a summary of the current context for the AI."""
        if not self.context:
            return ""
        
        summary_parts = ["\n\n---\n**User's Tax Data (from uploaded documents):**\n"]
        
        # Extract key financial information
        if "form16a" in self.context:
            data = self.context["form16a"]
            if isinstance(data, dict):
                summary_parts.append(f"- Gross Salary: ₹{data.get('gross_salary', 'N/A'):,}" if isinstance(data.get('gross_salary'), (int, float)) else f"- Gross Salary: {data.get('gross_salary', 'N/A')}")
                summary_parts.append(f"- TDS Deducted: ₹{data.get('tds_deducted', 'N/A'):,}" if isinstance(data.get('tds_deducted'), (int, float)) else f"- TDS Deducted: {data.get('tds_deducted', 'N/A')}")
        
        if "form16b" in self.context:
            data = self.context["form16b"]
            if isinstance(data, dict):
                summary_parts.append(f"- Chapter VI-A Deductions: ₹{data.get('chapter_vi_a', 'N/A'):,}" if isinstance(data.get('chapter_vi_a'), (int, float)) else "")
        
        if "ais" in self.context:
            data = self.context["ais"]
            if isinstance(data, dict):
                summary_parts.append(f"- Interest Income: ₹{data.get('interest_income', 'N/A'):,}" if isinstance(data.get('interest_income'), (int, float)) else "")
                summary_parts.append(f"- Dividend Income: ₹{data.get('dividend_income', 'N/A'):,}" if isinstance(data.get('dividend_income'), (int, float)) else "")
        
        # Handle flat structure
        for key in ['gross_salary', 'other_income', 'ch_via', 'tds_deducted']:
            if key in self.context and key not in str(summary_parts):
                value = self.context[key]
                if isinstance(value, (int, float)):
                    label = key.replace('_', ' ').title()
                    if key == 'ch_via':
                        label = 'Chapter VI-A Deductions'
                    summary_parts.append(f"- {label}: ₹{value:,}")
        
        return "\n".join([p for p in summary_parts if p])
    
    def to_api_messages(self) -> List[Dict[str, str]]:
        """Convert session to OpenRouter API format."""
        api_messages = [{"role": "system", "content": TAXMATE_SYSTEM_PROMPT}]
        
        # Add context to the first user message if available
        context_info = self.get_context_summary()
        
        for i, msg in enumerate(self.messages):
            content = msg.content
            # Prepend context to first user message
            if i == 0 and msg.role == "user" and context_info:
                content = f"{context_info}\n\n---\n**User Question:** {content}"
            api_messages.append({"role": msg.role, "content": content})
        
        return api_messages

# ============================================================
# Chat Service
# ============================================================
class ChatService:
    """Main chat service for TaxMate."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.session = ChatSession()
        
        if not OPENROUTER_API_KEY:
            chat_logger.warning("OPENROUTER_API_KEY not found!")
    
    def set_context(self, context: Dict[str, Any]) -> str:
        """Set document context for personalized responses."""
        self.session.set_context(context)
        return "I've received your tax document data. I can now provide personalized advice based on your specific situation. What would you like to know?"
    
    def load_context_from_db(self, user_id: str) -> bool:
        """Load tax context directly from DB for the user."""
        try:
            from app.services.db_helpers import load_user_tax_data
            from app.db.connection import get_sync_db
            
            db = get_sync_db()
            context = load_user_tax_data(db, user_id)
            
            if context:
                self.session.set_context(context)
                chat_logger.info(f"Loaded DB context for user {user_id}")
                return True
            else:
                chat_logger.warning(f"No context found in DB for user {user_id}")
                return False
        except Exception as e:
            chat_logger.error(f"Failed to load DB context: {e}")
            return False

    def clear_context(self) -> None:
        """Clear the current context."""
        self.session.context = None
        chat_logger.info("Context cleared")
    
    def clear_history(self) -> None:
        """Clear chat history while preserving context."""
        self.session.messages = []
        chat_logger.info("Chat history cleared")
    
    def get_response(self, user_message: str) -> str:
        """
        Get AI response for a user message.
        
        Args:
            user_message: The user's question/message
            
        Returns:
            AI assistant's response text
        """
        if not OPENROUTER_API_KEY:
            return "Error: OpenRouter API key not configured. Please set OPENROUTER_API_KEY in .env file."
        
        try:
            # Add user message to session
            self.session.add_user_message(user_message)
            
            # Convert to API format
            api_messages = self.session.to_api_messages()
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": api_messages,
            }
            
            chat_logger.info(f"Sending request to OpenRouter (model: {self.model})")
            
            # Make API call with timeout
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            # Extract assistant message
            if "choices" in response_data and len(response_data["choices"]) > 0:
                assistant_message = response_data["choices"][0]["message"]["content"]
                
                # Add to session history
                self.session.add_assistant_message(assistant_message)
                
                chat_logger.info("Successfully received response from OpenRouter")
                return assistant_message
            else:
                error_msg = "Unexpected response format from OpenRouter API"
                chat_logger.error(f"{error_msg}: {response_data}")
                return f"Error: {error_msg}"
                
        except requests.exceptions.Timeout:
            error_msg = "Request to AI service timed out. Please try again."
            chat_logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to AI service: {str(e)}"
            chat_logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            chat_logger.error(error_msg)
            return f"Error: {error_msg}"

    # ... get_response logic remains check for context inside session
    def has_context(self) -> bool:
        """Check if context is available."""
        return self.session.context is not None

# ============================================================
# Convenience Functions
# ============================================================
def create_chat_service(model: str = DEFAULT_MODEL) -> ChatService:
    """Factory function to create a new chat service instance."""
    return ChatService(model=model)

# ============================================================
# Main (for testing)
# ============================================================
if __name__ == "__main__":
    print("Testing TaxMate Chat Service...")
    
    service = ChatService()
    
    # Test without context
    print("\n--- Test 1: General Question ---")
    response = service.get_response("What is Section 80C?")
    print(f"Response: {response[:500]}...")
    
    # Test with context
    print("\n--- Test 2: With Context ---")
    service.set_context({
        "gross_salary": 1500000,
        "ch_via": 150000,
        "other_income": 50000
    })
    response = service.get_response("Which tax regime is better for me?")
    print(f"Response: {response[:500]}...")
