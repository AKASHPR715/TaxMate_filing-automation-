#!/usr/bin/env python3
"""
Jupyter-notebook friendly version with OpenRouter DeepSeek integration
"""
import json
from pathlib import Path
from openai import OpenAI
import time # Added for exponential backoff (good practice)
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# ============================================================
# Logging Configuration for tax_comparison.py
# ============================================================
def setup_comparison_logger():
    """Set up logging for tax comparison to separate log file."""
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tax_comparison.log"
    
    logger = logging.getLogger("tax_comparison")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with rotation
        fh = RotatingFileHandler(
            log_file, 
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding="utf-8"
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter(
            "%(levelname)s: %(message)s"
        ))
        logger.addHandler(ch)
    
    return logger

comparison_logger = setup_comparison_logger()

# ---------- helper: load JSON ----------
def load_json(file_name):
    """Load from the same folder the notebook is running in."""
    # Try exact path in current working directory first
    cwd_path = Path.cwd() / file_name
    try:
        if cwd_path.exists():
            comparison_logger.info(f"Loading JSON: {cwd_path}")
            with open(cwd_path, encoding='utf-8') as f:
                return json.load(f)

        # Fall back to project's data/extracted directory and pick the latest matching file
        REPO_ROOT = Path(__file__).resolve().parents[2]
        extracted_dir = REPO_ROOT / "data" / "extracted"
        if extracted_dir.exists():
            # exact filename in extracted dir
            extracted_exact = extracted_dir / file_name
            if extracted_exact.exists():
                with open(extracted_exact, encoding='utf-8') as f:
                    return json.load(f)

            # match timestamped files like `Form_16_Part_A_20251208_152605.json`
            stem = Path(file_name).stem
            candidates = sorted(extracted_dir.glob(f"{stem}*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if candidates:
                with open(candidates[0], encoding='utf-8') as f:
                    return json.load(f)

        print(f"Error: {file_name} not found in cwd or data/extracted. Please ensure it exists.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON from {file_name}.")
        return {}
    except Exception as e:
        print(f"Error loading {file_name}: {e}")
        return {}

# ---------- helpers: tax slabs ----------
def old_regime_tax(income):
    """Calculates tax liability under the old income tax regime (before cess)."""
    if income <= 250_000:
        return 0
    elif income <= 500_000:
        # Taxable income above 2,50,000 at 5%
        return (income - 250_000) * 0.05
    elif income <= 1_000_000:
        # Tax on 5,00,000 is 12,500 + tax on income above 5,00,000 at 20%
        return 12_500 + (income - 500_000) * 0.20
    else:
        # Tax on 10,00,000 is 1,12,500 + tax on income above 10,00,000 at 30%
        return 112_500 + (income - 1_000_000) * 0.30

def new_regime_tax(income):
    """Calculates tax liability under the new income tax regime (before cess) for FY 23-24 / AY 24-25."""
    # Note: New regime slabs effective from FY 23-24 (AY 24-25)
    if income <= 300_000: # Effective basic exemption limit for new regime
        return 0
    elif income <= 600_000:
        return (income - 300_000) * 0.05
    elif income <= 900_000:
        return 15_000 + (income - 600_000) * 0.10
    elif income <= 1_200_000:
        return 45_000 + (income - 900_000) * 0.15
    elif income <= 1_500_000:
        return 90_000 + (income - 1_200_000) * 0.20
    else:
        return 150_000 + (income - 1_500_000) * 0.30

# ---------- OpenRouter OpenAI Client Integration ----------
def get_ai_tax_analysis(tax_data, api_key, model="meta-llama/llama-3.3-70b-instruct:free"):
    """
    Get accounting analysis from a specified LLM via OpenRouter using the openai client.
    """
    if not api_key:
        return "⚠️ API Key not provided. Skipping AI analysis."

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Note: The original tax slab functions were simplified, so the prompt
    # should reflect the actual calculation for the analysis to be accurate.

    prompt = f"""As a tax accountant, analyze this Indian tax situation (FY 23-24 / AY 24-25) and provide actionable advice. Use the provided calculated figures:

Tax Calculation Summary:
- Gross Salary: ₹{tax_data['gross_salary']:,.0f}
- Other Income: ₹{tax_data['other_income']:,.0f}

OLD REGIME:
- Standard Deduction: ₹{tax_data['std_ded_old']:,.0f}
- Chapter VIA Deductions: ₹{tax_data['ch_via']:,.0f}
- Taxable Income: ₹{tax_data['old_taxable']:,.0f}
- Tax Liability (before cess): ₹{tax_data['old_tax']:,.0f}

NEW REGIME:
- Standard Deduction: ₹{tax_data['std_ded_new']:,.0f}
- Taxable Income: ₹{tax_data['new_taxable']:,.0f}
- Tax Liability (before cess): ₹{tax_data['new_tax']:,.0f}

Tax Difference: ₹{tax_data['tax_difference']:,.0f} (Old Tax - New Tax)

Provide:
1. Which regime is better (Lower Tax Liability is better) and why (based on the provided deductions).
2. Key tax-saving recommendations for the future.
3. Important compliance points.
4. Any red flags or areas of concern (e.g., high Other Income).
5. Action items before filing.

Keep response concise and actionable (max 400 words)."""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/tax-calculator",
                    "X-Title": "Indian Tax Calculator",
                },
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            ai_response = completion.choices[0].message.content
            return ai_response

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"❌ API Error on attempt {attempt + 1}: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"❌ AI Client Error after {max_retries} attempts: {str(e)}"
    return "Error: Exited retry loop unexpectedly."


# ---------- Tool Function for Orchestrator ----------
def compare_tax_regimes(extracted_data=None, gross_salary=None, other_income=None, ch_via=None):
    """
    Tool function to compare old vs new tax regimes.
    Can be called from orchestrator with extracted form data.
    
    Args:
        extracted_data: Dict of extracted form data
        gross_salary: Gross salary (optional, uses default if None)
        other_income: Other income (optional, uses default if None)
        ch_via: Chapter VIA deductions (optional, uses default if None)
    
    Returns:
        Dict with detailed tax calculation and explanation
    """
    comparison_logger.info("Starting tax regime comparison...")
    comparison_logger.info(f"Input - gross_salary: {gross_salary}, other_income: {other_income}, ch_via: {ch_via}")
    
    # Use provided values or load from JSON
    if gross_salary is None or other_income is None or ch_via is None:
        comparison_logger.info("Loading data from JSON files...")
        f16b = load_json("Form_16_Part_B.json")
        
        if gross_salary is None:
            gross_salary = 1_500_000
        if other_income is None:
            other_income = 100_000
        if ch_via is None:
            ch_via = 382402
        
        if f16b:
            if gross_salary == 1_500_000:  # Still default
                salary_present = f16b.get("salary_details", {}).get("total_salary", 0)
                salary_other = f16b.get("salary_details", {}).get("salary_from_other_employers", 0)
                gross_salary = salary_present + salary_other if (salary_present + salary_other) > 0 else 1_500_000
            
            if other_income == 100_000:  # Still default
                other_income = f16b.get("other_income_reported", {}).get("total_other_income", 0) or 100_000
    
    # Use extracted data if provided
    if extracted_data:
        for form_name, form_data in extracted_data.items():
            if "16_Part_B" in form_name and isinstance(form_data, dict):
                salary_details = form_data.get("salary_details", {})
                if isinstance(salary_details, dict):
                    gs = salary_details.get("total_salary", 0) + salary_details.get("salary_from_other_employers", 0)
                    if gs > 0:
                        gross_salary = gs
                
                other_income_data = form_data.get("other_income_reported", {})
                if isinstance(other_income_data, dict):
                    oi = other_income_data.get("total_other_income", 0)
                    if oi > 0:
                        other_income = oi
    
    # Constants for AY 24-25 (FY 23-24)
    std_ded_old = 50_000
    std_ded_new = 50_000
    
    # --- OLD REGIME CALCULATION ---
    salary_after_std_old = gross_salary - std_ded_old
    old_gti = salary_after_std_old + other_income
    old_taxable = max(old_gti - ch_via, 0)
    old_tax = old_regime_tax(old_taxable)
    
    # --- NEW REGIME CALCULATION ---
    salary_after_std_new = gross_salary - std_ded_new
    new_gti = salary_after_std_new + other_income
    new_taxable = max(new_gti, 0)
    new_tax = new_regime_tax(new_taxable)
    
    # Calculate difference
    tax_diff = old_tax - new_tax
    
    # Determine optimal regime
    if tax_diff > 0:
        optimal_regime = "NEW"
    elif tax_diff < 0:
        optimal_regime = "OLD"
    else:
        optimal_regime = "EQUAL"
    
    # Build detailed explanation
    detailed_explanation = []
    detailed_explanation.append("\n" + "="*70)
    detailed_explanation.append("OLD REGIME TAX CALCULATION (with deductions like 80C, 80D, etc.)")
    detailed_explanation.append("="*70)
    detailed_explanation.append(f"  Gross Salary (present + other)      : ₹ {gross_salary:,.0f}")
    detailed_explanation.append(f"  Less: Standard deduction (u/s 16)   : ₹ {std_ded_old:,.0f}")
    detailed_explanation.append(f"  Salary after standard deduction     : ₹ {salary_after_std_old:,.0f}")
    detailed_explanation.append(f"  Other income                        : ₹ {other_income:,.0f}")
    detailed_explanation.append(f"  Gross total income                  : ₹ {old_gti:,.0f}")
    detailed_explanation.append(f"  Less: Deductions (80C, 80D, etc.)   : ₹ {ch_via:,.0f}")
    detailed_explanation.append(f"  Taxable income (old)                : ₹ {old_taxable:,.0f}")
    detailed_explanation.append(f"  TAX LIABILITY (before cess)         : ₹ {old_tax:,.0f} ✓")
    
    detailed_explanation.append("\n" + "="*70)
    detailed_explanation.append("NEW REGIME TAX CALCULATION (Simplified - No deductions allowed)")
    detailed_explanation.append("="*70)
    detailed_explanation.append(f"  Gross Salary (present + other)      : ₹ {gross_salary:,.0f}")
    detailed_explanation.append(f"  Less: Standard deduction (u/s 16)   : ₹ {std_ded_new:,.0f}")
    detailed_explanation.append(f"  Salary after standard deduction     : ₹ {salary_after_std_new:,.0f}")
    detailed_explanation.append(f"  Other income                        : ₹ {other_income:,.0f}")
    detailed_explanation.append(f"  Gross total income                  : ₹ {new_gti:,.0f}")
    detailed_explanation.append(f"  Less: Deductions (No deductions)    : ₹ 0")
    detailed_explanation.append(f"  Taxable income (new)                : ₹ {new_taxable:,.0f}")
    detailed_explanation.append(f"  TAX LIABILITY (before cess)         : ₹ {new_tax:,.0f} ✓")
    
    detailed_explanation.append("\n" + "="*70)
    detailed_explanation.append("REGIME COMPARISON & ANALYSIS")
    detailed_explanation.append("="*70)
    detailed_explanation.append(f"  Old Regime Taxable Income           : ₹ {old_taxable:,.0f}")
    detailed_explanation.append(f"  New Regime Taxable Income           : ₹ {new_taxable:,.0f}")
    detailed_explanation.append(f"  Difference                          : ₹ {new_taxable - old_taxable:,.0f}")
    detailed_explanation.append("")
    detailed_explanation.append(f"  Old Regime Tax                      : ₹ {old_tax:,.0f}")
    detailed_explanation.append(f"  New Regime Tax                      : ₹ {new_tax:,.0f}")
    detailed_explanation.append(f"  Tax Difference (old - new)          : ₹ {tax_diff:,.0f}")
    
    # Add recommendations based on regime
    if optimal_regime == "NEW":
        detailed_explanation.append("")
        detailed_explanation.append(f"  🎯 OPTIMAL REGIME: NEW REGIME")
        detailed_explanation.append(f"  💡 Tax Savings: ₹ {abs(tax_diff):,.0f}")
        detailed_explanation.append(f"     → New regime saves you ₹{abs(tax_diff):,.0f} per year!")
    elif optimal_regime == "OLD":
        detailed_explanation.append("")
        detailed_explanation.append(f"  🎯 OPTIMAL REGIME: OLD REGIME")
        detailed_explanation.append(f"  💡 Tax Savings: ₹ {abs(tax_diff):,.0f}")
        detailed_explanation.append(f"     → Old regime saves you ₹{abs(tax_diff):,.0f} per year!")
    else:
        detailed_explanation.append("")
        detailed_explanation.append(f"  ⚖️  BOTH REGIMES EQUAL")
        detailed_explanation.append(f"     → Both regimes result in the same tax liability")
    
    detailed_explanation.append("\n" + "="*70)
    detailed_explanation.append("WAYS TO REDUCE YOUR TAX LIABILITY")
    detailed_explanation.append("="*70)
    
    # Suggestions based on regime
    if optimal_regime == "OLD":
        detailed_explanation.append("\n🔹 MAXIMIZE DEDUCTIONS (Old Regime Strategy):")
        detailed_explanation.append("   1. Section 80C - Invest up to ₹1,50,000 in:")
        detailed_explanation.append("      • Life Insurance premiums")
        detailed_explanation.append("      • PPF (Public Provident Fund)")
        detailed_explanation.append("      • ELSS (Equity Linked Saving Scheme)")
        detailed_explanation.append("      • Tuition fees for children")
        detailed_explanation.append("   2. Section 80D - Health Insurance premiums (₹25,000 - ₹50,000)")
        detailed_explanation.append("   3. Section 80CCD(1B) - NPS contribution (additional ₹50,000)")
        detailed_explanation.append("   4. Section 80E - Education loan interest deduction")
        detailed_explanation.append("   5. Section 80G - Charitable donations deduction")
        deduction_increase_potential = ch_via * 0.10  # 10% more deductions
        detailed_explanation.append(f"\n   💰 Potential savings if you increase deductions by 10%:")
        detailed_explanation.append(f"       → Extra ₹{int(deduction_increase_potential):,.0f} deduction")
        detailed_explanation.append(f"       → Tax saving: ₹{int(deduction_increase_potential * 0.20):,.0f} (at 20% slab)")
    else:
        detailed_explanation.append("\n🔹 NEW REGIME OPTIMIZATION:")
        detailed_explanation.append("   Since you're in New Regime, standard deductions don't apply.")
        detailed_explanation.append("   Focus on:")
        detailed_explanation.append("   • Controlling your Other Income")
        detailed_explanation.append("   • Consider shifting to Old Regime if you plan more investments")
        detailed_explanation.append("   • Review at year-end which regime is more beneficial")
    
    detailed_explanation.append("\n" + "="*70)
    
    explanation_text = "\n".join(detailed_explanation)
    
    return {
        "gross_salary": gross_salary,
        "other_income": other_income,
        "std_ded_old": std_ded_old,
        "std_ded_new": std_ded_new,
        "ch_via": ch_via,
        "old_taxable": old_taxable,
        "old_tax": old_tax,
        "new_taxable": new_taxable,
        "new_tax": new_tax,
        "tax_diff": tax_diff,
        "optimal_regime": optimal_regime,
        "detailed_explanation": explanation_text,
    }


# ---------- main ----------
def main(openrouter_api_key='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'):
    """
    Main function - pass your OpenRouter API key as parameter

    Get your free API key from: https://openrouter.ai/keys

    Usage:
        # Without AI (your current output only)
        # main()

        # With AI analysis
        # main(openrouter_api_key="sk-or-v1-xxxxx")
    """
    # Load placeholder data (assuming these JSON files exist for execution)
    f16a = load_json("Form_16_Part_A.json")
    f16b = load_json("Form_16_Part_B.json")
    ais  = load_json("Form_AIS.json")

    # Use default values if files were not found/loaded properly
    gross_salary = 1_500_000 # Default gross salary
    other_income = 100_000 # Default other income
    ch_via = 382402 # Default Ch-VIA deductions

    if f16b:
        salary_present   = f16b.get("salary_details", {}).get("total_salary", 0)
        salary_other     = f16b.get("salary_details", {}).get("salary_from_other_employers", 0)
        gross_salary     = salary_present + salary_other
        other_income     = f16b.get("other_income_reported", {}).get("total_other_income", 0)
        # Placeholder/Example for Chapter VIA - you'd usually calculate this dynamically
        # based on 80C, 80D, etc., but we use the hardcoded value from the original script
        ch_via = 382402


    # Constants for AY 24-25 (FY 23-24)
    # Note: Standard deduction of 50k is applicable to both regimes for AY 24-25
    std_ded_old = 50_000
    std_ded_new = 50_000

    # --- OLD REGIME CALCULATION ---
    salary_after_std_old = gross_salary - std_ded_old
    old_gti     = salary_after_std_old + other_income
    old_taxable = max(old_gti - ch_via, 0)
    old_tax     = old_regime_tax(old_taxable)

    # --- NEW REGIME CALCULATION ---
    salary_after_std_new = gross_salary - std_ded_new
    new_gti     = salary_after_std_new + other_income
    # No Chapter VIA deductions allowed in the new regime
    new_taxable = max(new_gti, 0)
    new_tax     = new_regime_tax(new_taxable)

    # --- PRETTY PRINTING ---
    print("\n" + "="*60)
    print("📊 TAX CALCULATION REPORT")
    print("="*60)

    print("\nOLD REGIME (with HRA, LTA, 80C, etc. benefits):")
    print("-" * 60)
    print(f"  Gross Salary (present + other)      : ₹ {gross_salary:,.0f}")
    print(f"  Less: Standard deduction (u/s 16)   : ₹ {std_ded_old:,.0f}")
    print(f"  Salary after standard deduction     : ₹ {salary_after_std_old:,.0f}")
    print(f"  Other income                        : ₹ {other_income:,.0f}")
    print(f"  Gross total income                  : ₹ {old_gti:,.0f}")
    print(f"  Less: Deductions ch-VIA (e.g., 80C) : ₹ {ch_via:,.0f}")
    print(f"  Taxable income (old)                : ₹ {old_taxable:,.0f}")
    print(f"  Tax (before cess)                   : ₹ {old_tax:,.0f}")

    print("\nNEW REGIME (Simplified/Default Tax):")
    print("-" * 60)
    print(f"  Gross Salary (present + other)      : ₹ {gross_salary:,.0f}")
    print(f"  Less: Standard deduction (u/s 16)   : ₹ {std_ded_new:,.0f}")
    print(f"  Salary after standard deduction     : ₹ {salary_after_std_new:,.0f}")
    print(f"  Other income                        : ₹ {other_income:,.0f}")
    print(f"  Gross total income                  : ₹ {new_gti:,.0f}")
    print(f"  Taxable income (new)                : ₹ {new_taxable:,.0f}")
    print(f"  Tax (before cess)                   : ₹ {new_tax:,.0f}")

    print("\nCOMPARISON:")
    print("-" * 60)
    print(f"  Taxable income – old | new          : ₹ {old_taxable:,.0f} | ₹ {new_taxable:,.0f}")
    print(f"  Tax – old | new                     : ₹ {old_tax:,.0f} | ₹ {new_tax:,.0f}")
    tax_diff = old_tax - new_tax
    print(f"  Difference (old - new)              : ₹ {tax_diff:,.0f}")

    if tax_diff > 0:
        print(f"  💡 New regime saves you             : ₹ {abs(tax_diff):,.0f}")
    elif tax_diff < 0:
        print(f"  💡 Old regime saves you             : ₹ {abs(tax_diff):,.0f}")
    else:
        print("  💡 Both regimes result in the same tax liability.")

    print("="*60)

    # Get AI Analysis if API key provided
    if openrouter_api_key and openrouter_api_key == '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': # Check for default
        print("\n" + "="*60)
        print("🤖 AI TAX ADVISOR (Llama 3.3 70B Analysis via OpenAI Client)")
        print("="*60 + "\n")

        tax_data = {
            'gross_salary': gross_salary,
            'other_income': other_income,
            'std_ded_old': std_ded_old,
            'std_ded_new': std_ded_new,
            'ch_via': ch_via,
            'old_taxable': old_taxable,
            'old_tax': old_tax,
            'new_taxable': new_taxable,
            'new_tax': new_tax,
            'tax_difference': tax_diff
        }

        print("Analyzing your tax situation... ⏳\n")
        analysis = get_ai_tax_analysis(tax_data, openrouter_api_key)
        print(analysis)
        print("\n" + "="*60)
    else:
        print("\n💡 Tip: Pass your OpenRouter API key to get AI tax analysis.")
        print("   Usage: main(openrouter_api_key='sk-or-v1-xxxxx')")
        print("   Get free key: https://openrouter.ai/keys")

    # --- Log the operation to a separate tax_comparison log file (not answers.log) ---
    try:
        summary = []
        summary.append("TAX CALCULATION REPORT")
        summary.append("=" * 40)
        summary.append(f"Timestamp: {datetime.now().isoformat()}")
        summary.append(f"Gross Salary: {gross_salary}")
        summary.append(f"Other Income: {other_income}")
        summary.append(f"Old regime - Taxable: {old_taxable}, Tax (before cess): {old_tax}")
        summary.append(f"New regime - Taxable: {new_taxable}, Tax (before cess): {new_tax}")
        summary.append(f"Difference (old - new): {tax_diff}")
        if 'analysis' in locals() and analysis:
            summary.append("")
            summary.append("AI Analysis:")
            summary.append(analysis)

        log_dir = Path(__file__).resolve().parents[2] / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "tax_comparison.log"
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write("\n" + "\n".join(str(s) for s in summary) + "\n")
            lf.write("-" * 60 + "\n")
    except Exception:
        # Best-effort only; do not interrupt normal flow
        pass


# Run the analysis (using default key/no key for execution)
main()
