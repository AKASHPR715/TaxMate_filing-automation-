
# FY 2024-25 Tax Slabs & Limits

# Old Regime Slabs (FY25 is same as previous for Old)
OLD_REGIME_SLABS = [
    (250000, 0.0),
    (500000, 0.05),
    (1000000, 0.20),
    (float('inf'), 0.30)
]

# New Regime Slabs (FY25 Budget 2024 Updates)
# Upto 3L: Nil, 3-7L: 5%, 7-10L: 10%, 10-12L: 15%, 12-15L: 20%, >15L: 30%
NEW_REGIME_SLABS = [
    (300000, 0.0),
    (700000, 0.05),
    (1000000, 0.10),
    (1200000, 0.15),
    (1500000, 0.20),
    (float('inf'), 0.30)
]

# Limits
SECTION_80C_LIMIT = 150000
STANDARD_DEDUCTION = 75000  # Increased to 75k in New Regime (Budget 2024), was 50k
OLD_REGIME_STANDARD_DEDUCTION = 50000

# Surcharge (Simplified for research)
SURCHARGE_RATES = [
    (5000000, 0.10),
    (10000000, 0.15),
    (20000000, 0.25),   # 25% for >2Cr in Old, capped at 25% for New
    (50000000, 0.37)    # 37% for >5Cr (Only valid for Old Regime now, New is capped at 25%)
]

# Cess
HEALTH_AND_EDUCATION_CESS = 0.04
