"""
Gemini Vision-based PDF Extraction Service
Fast extraction using Google's Gemini Vision model - 6-12x faster than LlamaExtract
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Type, List
from datetime import datetime
from pydantic import BaseModel

# Gemini imports
import google.generativeai as genai
from pdf2image import convert_from_path
from PIL import Image

from dotenv import load_dotenv

# Load environment
load_dotenv()

logger = logging.getLogger("gemini_extraction")

# ============================================================
# Configuration
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not found in .env - Gemini extraction will not work")

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# ============================================================
# Schema Prompts for Different Document Types
# ============================================================

FORM16A_SCHEMA = """
Extract all information from this Form 16 Part A (TDS Certificate) and return as JSON with this structure:

{
  "employer_details": {
    "name": "string",
    "address": "string",
    "TAN": "string (10 chars, format: AAAA12345A)",
    "PAN": "string (10 chars)"
  },
  "employee_details": {
    "name": "string",
    "PAN": "string (10 chars, format: AAAAA1234A)",
    "address": "string"
  },
  "assessment_details": {
    "financial_year": "string (e.g., 2023-24)",
    "assessment_year": "string (e.g., 2024-25)"
  },
  "tds_summary": [
    {
      "quarter": "string (Q1/Q2/Q3/Q4)",
      "period": "string",
      "amount_paid_credited": "number",
      "tax_deducted": "number",
      "deposit_date": "string (YYYY-MM-DD)"
    }
  ],
  "total_tds": "number"
}

Important:
- Extract ALL numeric values as numbers, not strings
- Dates in YYYY-MM-DD format
- Include all quarters present in the document
- Be precise with TAN and PAN formats
"""

FORM16B_SCHEMA = """
Extract all information from this Form 16 Part B and return as JSON with this structure:

{
  "employer_details": {
    "name": "string",
    "address": "string",
    "TAN": "string",
    "PAN": "string"
  },
  "employee_details": {
    "name": "string",
    "PAN": "string",
    "address": "string",
    "designation": "string"
  },
  "salary_details": {
    "gross_salary": "number",
    "allowances": "number",
    "perquisites": "number",
    "profits_in_lieu_of_salary": "number",
    "total_salary": "number",
    "salary_from_other_employers": "number"
  },
  "exemptions_u_s_10": {
    "house_rent_allowance": "number",
    "leave_travel_concession": "number",
    "gratuity": "number",
    "leave_encashment": "number",
    "commuted_pension": "number",
    "any_other_exemption": "number",
    "total_exemptions": "number"
  },
  "deductions_u_s_16": {
    "standard_deduction": "number",
    "entertainment_allowance": "number",
    "professional_tax": "number",
    "total_deductions": "number"
  },
  "other_income_reported": {
    "house_property_income": "number",
    "total_other_income": "number"
  },
  "deductions_chapter_VIA": {
    "section_80C": "number",
    "section_80CCC": "number",
    "section_80CCD_1": "number",
    "section_80CCD_1B": "number",
    "section_80CCD_2": "number",
    "section_80D": "number",
    "section_80E": "number",
    "section_80G": "number",
    "section_80TTA": "number",
    "any_other_deductions": "number",
    "total_deductions_via": "number"
  },
  "tax_computation": {
    "total_income": "number",
    "total_tax_payable": "number",
    "rebate_u_s_87a": "number",
    "surcharge": "number",
    "education_cess": "number",
    "tax_deducted_at_source": "number",
    "total_tax_paid": "number"
  }
}

Important:
- All amounts must be numbers (not strings)
- If a field is not present, use 0
- Extract values carefully from tables
- Verify calculations if possible
"""

AIS_SCHEMA = """
Extract all information from this Annual Information Statement (AIS) and return as JSON:

{
  "assessee_details": {
    "name": "string",
    "PAN": "string",
    "address": "string",
    "financial_year": "string",
    "assessment_year": "string"
  },
  "salary_income": [
    {
      "employer_name": "string",
      "employer_tan": "string",
      "gross_salary": "number",
      "tds_deducted": "number"
    }
  ],
  "interest_income": [
    {
      "bank_or_entity_name": "string",
      "account_number": "string",
      "interest_amount": "number",
      "tds_deducted": "number"
    }
  ],
  "dividend_income": [
    {
      "company_name": "string",
      "dividend_amount": "number",
      "tds_deducted": "number"
    }
  ],
  "securities_transactions": [
    {
      "transaction_type": "string (Sale/Purchase)",
      "transaction_date": "string (YYYY-MM-DD)",
      "script_name": "string",
      "isin_code": "string",
      "quantity": "number",
      "transaction_value": "number",
      "exchange": "string"
    }
  ],
  "mutual_fund_transactions": [
    {
      "transaction_type": "string",
      "transaction_date": "string",
      "fund_name": "string",
      "units": "number",
      "amount": "number"
    }
  ],
  "total_tds": "number"
}

Important:
- Extract all transactions from tables
- Dates in YYYY-MM-DD format
- All amounts as numbers
- If section is not present, use empty array []
"""


# ============================================================
# Gemini Vision Extractor
# ============================================================

class GeminiVisionExtractor:
    """Fast PDF extraction using Gemini Vision model"""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini Vision extractor
        
        Args:
            model_name: Gemini model to use
                - gemini-1.5-flash: Fastest, good accuracy (recommended)
                - gemini-1.5-pro: Better accuracy, slightly slower
        """
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set in environment variables")
        
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        logger.info(f"Initialized Gemini extractor with model: {model_name}")
    
    def extract_pdf(
        self, 
        pdf_path: str, 
        schema_prompt: str,
        max_pages: int = 5,
        dpi: int = 200
    ) -> Dict[str, Any]:
        """
        Extract structured data from PDF using vision model
        
        Args:
            pdf_path: Path to PDF file
            schema_prompt: Extraction schema instructions
            max_pages: Maximum pages to process (default 5)
            dpi: Image resolution (higher = better quality but slower)
            
        Returns:
            Extracted data as dictionary
        """
        logger.info(f"Starting Gemini extraction for: {pdf_path}")
        start_time = datetime.now()
        
        try:
            # Convert PDF to images
            logger.info(f"Converting PDF to images (dpi={dpi})...")
            images = convert_from_path(
                pdf_path, 
                dpi=dpi,
                first_page=1,
                last_page=min(max_pages, 10)  # Safety limit
            )
            logger.info(f"Converted {len(images)} pages to images")
            
            # For multi-page documents, combine or process separately
            if len(images) == 1:
                result = self._extract_from_image(images[0], schema_prompt)
            else:
                # For multi-page, send all images to model
                result = self._extract_from_images(images, schema_prompt)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Extraction completed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise
    
    def _extract_from_image(self, image: Image.Image, schema_prompt: str) -> Dict[str, Any]:
        """Extract from single image"""
        prompt = f"""{schema_prompt}

Return ONLY valid JSON. No explanations, no markdown, just the JSON object."""
        
        logger.info("Calling Gemini Vision API (single image)...")
        response = self.model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                temperature=0.1,  # Low temperature for consistency
                top_p=0.95,
                max_output_tokens=8192,
            )
        )
        
        return self._parse_json_response(response.text)
    
    def _extract_from_images(self, images: List[Image.Image], schema_prompt: str) -> Dict[str, Any]:
        """Extract from multiple images"""
        prompt = f"""Analyze all {len(images)} pages of this document and extract the complete information.

{schema_prompt}

Combine information from all pages. Return ONLY valid JSON."""
        
        logger.info(f"Calling Gemini Vision API ({len(images)} images)...")
        
        # Build content list: [prompt, img1, img2, ...]
        content = [prompt] + images
        
        response = self.model.generate_content(
            content,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                max_output_tokens=8192,
            )
        )
        
        return self._parse_json_response(response.text)
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Gemini response, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            # Parse JSON
            data = json.loads(json_str)
            logger.info("Successfully parsed JSON response")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")


# ============================================================
# Convenience Functions
# ============================================================

def extract_form16a_vision(pdf_path: str) -> Dict[str, Any]:
    """Extract Form 16 Part A using Gemini Vision"""
    extractor = GeminiVisionExtractor()
    return extractor.extract_pdf(pdf_path, FORM16A_SCHEMA, max_pages=2)


def extract_form16b_vision(pdf_path: str) -> Dict[str, Any]:
    """Extract Form 16 Part B using Gemini Vision"""
    extractor = GeminiVisionExtractor()
    return extractor.extract_pdf(pdf_path, FORM16B_SCHEMA, max_pages=3)


def extract_ais_vision(pdf_path: str) -> Dict[str, Any]:
    """Extract AIS using Gemini Vision"""
    extractor = GeminiVisionExtractor()
    return extractor.extract_pdf(pdf_path, AIS_SCHEMA, max_pages=5)


# ============================================================
# Testing
# ============================================================

if __name__ == "__main__":
    # Test extraction
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python gemini_vision_extraction.py <pdf_path> <doc_type>")
        print("doc_type: form16a | form16b | ais")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    doc_type = sys.argv[2].lower()
    
    print(f"Testing Gemini Vision extraction on {pdf_path}")
    print(f"Document type: {doc_type}")
    
    if doc_type == "form16a":
        result = extract_form16a_vision(pdf_path)
    elif doc_type == "form16b":
        result = extract_form16b_vision(pdf_path)
    elif doc_type == "ais":
        result = extract_ais_vision(pdf_path)
    else:
        print(f"Unknown doc type: {doc_type}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("EXTRACTION RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))
