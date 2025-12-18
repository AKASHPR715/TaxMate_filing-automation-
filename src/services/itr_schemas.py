"""
Official ITR JSON Schema Templates (AY 2025-26)
Strictly based on ITR-1_2025_Main_V1.1.json and ITR-2_2025_Main_V1.1.json
"""

# ============================================================
# ITR-1 SAHAJ TEMPLATE (Based on V1.1 Schema)
# ============================================================
ITR1_TEMPLATE = {
    "ITR": {
        "ITR1": {
            "CreationInfo": {
                "SWVersionNo": "1.0",
                "SWCreatedBy": "SW00000001", # Pattern: [S][W][0-9]{8}
                "JSONCreatedBy": "SW00000001",
                "JSONCreationDate": "", # YYYY-MM-DD
                "IntermediaryCity": "Delhi",
                "Digest": "0000"
            },
            "Form_ITR1": {
                "FormName": "ITR-1",
                "Description": "For Individuals being a Resident (other than not ordinarily resident) having Total Income upto Rs.50 lakhs, having Income from Salaries, one house property, other sources (Interest etc.), and having agricultural income upto Rs.5 thousand",
                "AssessmentYear": "2025",
                "SchemaVer": "Ver1.1",
                "FormVer": "Ver1.1"
            },
            "PersonalInfo": {
                "AssesseeName": {
                    "FirstName": "",
                    "SurNameOrOrgName": "" 
                },
                "PAN": "",
                "Address": {
                    "ResidenceNo": "",
                    "LocalityOrArea": "",
                    "CityOrTownOrDistrict": "",
                    "StateCode": "",
                    "CountryCode": "91",
                    "CountryCodeMobile": 91,
                    "MobileNo": 0,
                    "EmailAddress": ""
                },
                "DOB": "", # YYYY-MM-DD
                "EmployerCategory": "OTH",
                "Status": "I" # Added inferred from schema usage context though mandatory in ITR2
            },
            "FilingStatus": {
                "ReturnFileSec": 11, # Integer 11 = 139(1)
                "OptOutNewTaxRegime": "N",
                "ItrFilingDueDate": "2025-07-31" # Pattern verified
            },
            "ITR1_IncomeDeductions": {
                "GrossSalary": 0,
                "IncomeFromSal": 0,
                "IncomeOthSrc": 0,
                "GrossTotIncome": 0,
                "UsrDeductUndChapVIA": {
                    "Section80C": 0,
                    "Section80CCC": 0,
                    "Section80CCD1": 0,
                    "Section80CCD1B": 0,
                    "Section80D": 0,
                    "Section80E": 0,
                    "Section80G": 0,
                    "Section80TTA": 0,
                    "TotalChapVIADed": 0
                },
                "DeductUndChapVIA": {
                    "Section80C": 0,
                    "Section80CCC": 0,
                    "Section80CCD1": 0,
                    "Section80CCD1B": 0,
                    "Section80D": 0,
                    "Section80E": 0,
                    "Section80G": 0,
                    "Section80TTA": 0,
                    "TotalChapVIADed": 0
                },
                "TotalIncome": 0
            },
            "ITR1_TaxComputation": {
                "TotalTaxPayable": 0,
                "Rebate87A": 0,
                "TaxPayableOnRebate": 0,
                "EducationCess": 0,
                "GrossTaxLiability": 0,
                "Section89": 0, # Required field
                "NetTaxLiability": 0,
                "TotalIntrstPay": 0,
                "TotTaxPlusIntrstPay": 0
            },
            "TaxPaid": {
                "TaxesPaid": [] 
            },
            "Refund": {
                "RefundDue": 0
            },
            "Verification": {
                "Declaration": {
                    "AssesseeName": "",
                    "FatherName": "", # Required
                    "Capacity": "S",
                    "Place": "INDIA",
                    "Date": ""
                }
            }
        }
    }
}

# ============================================================
# ITR-2 TEMPLATE (Based on V1.1 Schema)
# ============================================================
ITR2_TEMPLATE = {
    "ITR": {
        "ITR2": {
            "CreationInfo": {
                "SWVersionNo": "1.0",
                "SWCreatedBy": "SW00000001",
                "JSONCreatedBy": "SW00000001",
                "JSONCreationDate": "",
                "IntermediaryCity": "Delhi",
                "Digest": "0000"
            },
            "Form_ITR2": {
                "FormName": "ITR-2",
                "Description": "For Individuals and HUFs not having income from profits and gains of business or profession",
                "AssessmentYear": "2025",
                "SchemaVer": "Ver1.1",
                "FormVer": "Ver1.1"
            },
            "PartA_GEN1": {
                "PersonalInfo": {
                    "AssesseeName": {
                        "FirstName": "",
                        "MiddleName": "",
                        "SurNameOrOrgName": "" # Changed from SurName to match schema definition
                    },
                    "PAN": "",
                    "Address": {
                        "ResidenceNo": "",
                        "LocalityOrArea": "",
                        "CityOrTownOrDistrict": "",
                        "StateCode": "", 
                        "CountryCode": "91",
                        "CountryCodeMobile": 91,
                        "MobileNo": 0, # Integer
                        "EmailAddress": ""
                    },
                    "DOB": "",
                    "Status": "I"
                },
                "FilingStatus": {
                    "ReturnFileSec": 11,
                    "OptOutNewTaxRegime": "N",
                    "ResidentialStatus": "RES",
                    "ItrFilingDueDate": "2025-07-31" # Often required even if absent in some definitions
                }
            },
            "PartB-TI": {  # Note Hyphen
                "Salaries": 0,
                "IncomeFromHP": 0,
                "CapitalGains": 0,
                "IncomeFromOS": 0,
                "GrossTotalIncome": 0,
                "DeductionsUnderChapterVIA": {
                     "Section80C": 0,
                     "Section80CCC": 0,
                     "Section80CCD1": 0,
                     "Section80CCD1B": 0, 
                     "Section80D": 0,
                     "TotalChapVIADed": 0
                },
                "TotalIncome": 0
            },
            "PartB_TTI": { # Note Underscore
                "ComputationOfTaxLiability": {
                    "TaxPayableOnTotalIncome": 0,
                    "Rebate87A": 0,
                    "TaxPayableAfterRebate": 0,
                    "HealthAndEducationCess": 0,
                    "GrossTaxLiability": 0,
                    "NetTaxLiability": 0,
                    "TotalTaxPayable": 0
                }
            },
            "ScheduleS": {
                "Salaries": []
            },
            "ScheduleCYLA": { # Required
                 "TotalCurrYrLosses": 0
            },
            "ScheduleBFLA": { # Required
                 "TotalBFLA": 0
            },
             "ScheduleCGFor23": { # Often conditioned, but let's keep skeletal
            },
            "ScheduleHP": {
                "IncFromOtherSources": { "GrossInterest": 0 }
            },
            "ScheduleTDS1": {
                "TDS1": []
            },
            "ScheduleOS": {
                "IncOthSrc": []
            },
            "Verification": {
                "Declaration": {
                    "AssesseeName": "",
                    "FatherName": "",
                    "Capacity": "S",
                    "Place": "INDIA",
                    "Date": ""
                }
            }
        }
    }
}
