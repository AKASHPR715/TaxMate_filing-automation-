#!/usr/bin/env python3
"""
Quick Tax Calculator for Manual Verification
Run this to verify any of the examples from the verification document
"""

def calculate_hra_exemption(basic: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
    """Calculate HRA exemption under Section 10(13A)"""
    if rent_paid <= 0:
        return 0.0
    
    option_a = hra_received
    option_b = basic * (0.50 if is_metro else 0.40)
    option_c = max(0, rent_paid - (0.10 * basic))
    
    exemption = min(option_a, option_b, option_c)
    
    print(f"\nHRA Exemption Calculation:")
    print(f"  Option A (Actual HRA): ₹{option_a:,.2f}")
    print(f"  Option B ({'50%' if is_metro else '40%'} of Basic): ₹{option_b:,.2f}")
    print(f"  Option C (Rent - 10% Basic): ₹{option_c:,.2f}")
    print(f"  HRA Exemption = Min(A, B, C) = ₹{exemption:,.2f}")
    
    return exemption

def old_regime_tax(income: float) -> float:
    """Old regime tax calculation (before cess)"""
    if income <= 250_000:
        return 0
    elif income <= 500_000:
        return (income - 250_000) * 0.05
    elif income <= 1_000_000:
        return 12_500 + (income - 500_000) * 0.20
    else:
        return 112_500 + (income - 1_000_000) * 0.30

def new_regime_tax_24_25(income: float) -> float:
    """New regime tax for FY 2024-25 (before cess)"""
    if income <= 300_000:
        return 0.0
    if income <= 700_000:
        return (income - 300_000) * 0.05
    if income <= 1_000_000:
        return 20_000 + (income - 700_000) * 0.10
    if income <= 1_200_000:
        return 50_000 + (income - 1_000_000) * 0.15
    if income <= 1_500_000:
        return 80_000 + (income - 1_200_000) * 0.20
    return 140_000 + (income - 1_500_000) * 0.30

def apply_cess(base_tax: float) -> float:
    """Add 4% health and education cess"""
    return base_tax * 1.04

def print_tax_breakdown(income: float, regime: str):
    """Print detailed tax breakdown"""
    if regime == "Old":
        if income <= 250_000:
            print(f"  ₹0 - ₹2,50,000: ₹0 (Exempt)")
        elif income <= 500_000:
            tax_slab2 = (income - 250_000) * 0.05
            print(f"  ₹2,50,001 - ₹{income:,.0f}: ₹{tax_slab2:,.2f} @ 5%")
        elif income <= 1_000_000:
            print(f"  ₹0 - ₹2,50,000: ₹0")
            print(f"  ₹2,50,001 - ₹5,00,000: ₹12,500 @ 5%")
            tax_slab3 = (income - 500_000) * 0.20
            print(f"  ₹5,00,001 - ₹{income:,.0f}: ₹{tax_slab3:,.2f} @ 20%")
        else:
            print(f"  ₹0 - ₹2,50,000: ₹0")
            print(f"  ₹2,50,001 - ₹5,00,000: ₹12,500 @ 5%")
            print(f"  ₹5,00,001 - ₹10,00,000: ₹1,00,000 @ 20%")
            tax_slab4 = (income - 1_000_000) * 0.30
            print(f"  ₹10,00,001 - ₹{income:,.0f}: ₹{tax_slab4:,.2f} @ 30%")
    else:  # New regime FY 24-25
        slabs = [
            (0, 300_000, 0.0),
            (300_000, 700_000, 0.05),
            (700_000, 1_000_000, 0.10),
            (1_000_000, 1_200_000, 0.15),
            (1_200_000, 1_500_000, 0.20),
            (1_500_000, float('inf'), 0.30)
        ]
        
        cumulative_tax = 0
        for lower, upper, rate in slabs:
            if income > lower:
                taxable_in_slab = min(income, upper) - lower
                tax_in_slab = taxable_in_slab * rate
                if rate == 0:
                    print(f"  ₹{lower:,} - ₹{min(income, upper):,.0f}: ₹0 (Exempt)")
                else:
                    print(f"  ₹{lower + 1:,} - ₹{min(income, upper):,.0f}: ₹{tax_in_slab:,.2f} @ {int(rate*100)}%")
                cumulative_tax += tax_in_slab
                if income <= upper:
                    break

# ============================================================================
# EXAMPLE 1: Simple Profile (Old Regime)
# ============================================================================
print("="*80)
print("EXAMPLE 1: Simple Profile (Old Regime)")
print("="*80)

gross_salary = 800_000
basic = 350_000
hra_received = 160_000
rent_paid = 120_000
is_metro = False
other_income = 0

pf = 42_000
elss = 50_000
lic = 30_000
medical_self = 15_000

print(f"\nInput:")
print(f"  Gross Salary: ₹{gross_salary:,}")
print(f"  Basic: ₹{basic:,}, HRA: ₹{hra_received:,}")
print(f"  Rent Paid: ₹{rent_paid:,} (Non-Metro)")
print(f"  Deductions: PF ₹{pf:,}, ELSS ₹{elss:,}, LIC ₹{lic:,}, Medical ₹{medical_self:,}")

hra_exemption = calculate_hra_exemption(basic, hra_received, rent_paid, is_metro)

print(f"\nStep-by-Step Calculation:")
print(f"1. Gross Salary: ₹{gross_salary:,}")
print(f"2. Less: HRA Exemption: ₹{hra_exemption:,}")
print(f"3. Less: Standard Deduction: ₹50,000")
income_after_std = gross_salary - hra_exemption - 50_000
print(f"4. Income from Salary: ₹{income_after_std:,}")
print(f"5. Add: Other Income: ₹{other_income:,}")
gti = income_after_std + other_income
print(f"6. Gross Total Income: ₹{gti:,}")

total_80c = min(pf + elss + lic, 150_000)
total_80d = medical_self
total_via = total_80c + total_80d
print(f"\n7. Chapter VI-A Deductions:")
print(f"   80C (PF+ELSS+LIC): ₹{pf + elss + lic:,} → capped at ₹{total_80c:,}")
print(f"   80D (Medical): ₹{total_80d:,}")
print(f"   Total: ₹{total_via:,}")

taxable = gti - total_via
print(f"\n8. Taxable Income: ₹{gti:,} - ₹{total_via:,} = ₹{taxable:,}")

print(f"\n9. Tax Calculation:")
print_tax_breakdown(taxable, "Old")

base_tax = old_regime_tax(taxable)
print(f"\n10. Base Tax: ₹{base_tax:,.2f}")

final_tax = apply_cess(base_tax)
print(f"11. Add 4% Cess: ₹{base_tax:,.2f} × 1.04 = ₹{final_tax:,.2f}")

print(f"\n{'='*80}")
print(f"FINAL ANSWER: ₹{final_tax:,.2f}")
print(f"{'='*80}")

# ============================================================================
# EXAMPLE 2: Medium Complexity (New Regime)
# ============================================================================
print("\n\n" + "="*80)
print("EXAMPLE 2: Medium Complexity (New Regime)")
print("="*80)

gross_salary2 = 1_200_000
other_income2 = 25_000

print(f"\nInput:")
print(f"  Gross Salary: ₹{gross_salary2:,}")
print(f"  Other Income: ₹{other_income2:,}")
print(f"  NOTE: New Regime - No HRA exemption, No Chapter VI-A deductions")

print(f"\nStep-by-Step Calculation:")
print(f"1. Gross Salary: ₹{gross_salary2:,}")
print(f"2. Less: Standard Deduction (FY 2024-25): ₹75,000")
income_after_std2 = gross_salary2 - 75_000
print(f"3. Income from Salary: ₹{income_after_std2:,}")
print(f"4. Add: Other Income: ₹{other_income2:,}")
gti2 = income_after_std2 + other_income2
print(f"5. Gross Total Income (= Taxable Income): ₹{gti2:,}")

print(f"\n6. Tax Calculation (New Regime FY 2024-25):")
print_tax_breakdown(gti2, "New")

base_tax2 = new_regime_tax_24_25(gti2)
print(f"\n7. Base Tax: ₹{base_tax2:,.2f}")

final_tax2 = apply_cess(base_tax2)
print(f"8. Add 4% Cess: ₹{base_tax2:,.2f} × 1.04 = ₹{final_tax2:,.2f}")

print(f"\n{'='*80}")
print(f"FINAL ANSWER: ₹{final_tax2:,.2f}")
print(f"{'='*80}")

print("\n\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)
print(f"\nExample 1 (Old Regime): ₹{final_tax:,.2f}")
print(f"Example 2 (New Regime): ₹{final_tax2:,.2f}")
print("\nThese should match the values in experimental_verification.md")
print("You can verify using any online Indian tax calculator for FY 2024-25")
print("="*80)
