"""
Default Values Configuration for TaxMate
Centralized default values to avoid magic numbers in code.
"""
import os
from typing import Dict, Any

# ============================================================
# Personal Information Defaults
# ============================================================

# Default values for development/testing
# These should be overridden in production with real values
DEV_DEFAULTS = {
    "aadhaar": "123456789012",
    "mobile": "9999999999",
    "email": "test@example.com",
    "father_name": "FATHER NAME",
    "dob": "1990-01-01",
}

# Load from environment if available
PRODUCTION_MODE = os.getenv("ENVIRONMENT", "development").lower() == "production"

DEFAULT_AADHAAR = os.getenv("DEFAULT_AADHAAR", DEV_DEFAULTS["aadhaar"])
DEFAULT_MOBILE = os.getenv("DEFAULT_MOBILE", DEV_DEFAULTS["mobile"])
DEFAULT_EMAIL = os.getenv("DEFAULT_EMAIL", DEV_DEFAULTS["email"])
DEFAULT_FATHER_NAME = os.getenv("DEFAULT_FATHER_NAME", DEV_DEFAULTS["father_name"])
DEFAULT_DOB = os.getenv("DEFAULT_DOB", DEV_DEFAULTS["dob"])

# ============================================================
# Warning Messages
# ============================================================

def get_default_value_warning(field_name: str) -> str:
    """Generate warning message for use of default values."""
    if PRODUCTION_MODE:
        return f"⚠️  PRODUCTION WARNING: Using default value for {field_name}. This should be provided by user."
    return f"ℹ️  Using development default for {field_name}"


def get_defaults_dict() -> Dict[str, Any]:
    """
    Get all default values as a dictionary.
    
    Returns:
        Dictionary with all default values
    """
    return {
        "aadhaar": DEFAULT_AADHAAR,
        "mobile": int(DEFAULT_MOBILE),
        "email": DEFAULT_EMAIL,
        "father_name": DEFAULT_FATHER_NAME,
        "dob": DEFAULT_DOB,
    }


# ============================================================
# Validation
# ============================================================

def is_default_value(value: Any, field_name: str) -> bool:
    """
    Check if a value is a default/placeholder value.
    
    Args:
        value: Value to check
        field_name: Name of the field
        
    Returns:
        True if value is a default placeholder
    """
    defaults = get_defaults_dict()
    
    # Convert to string for comparison
    str_value = str(value)
    
    if field_name in defaults:
        return str_value == str(defaults[field_name])
    
    return False
