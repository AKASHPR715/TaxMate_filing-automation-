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
                "SWVersionNo": "1.1",
                "SWCreatedBy": "SW00000001",
                "JSONCreatedBy": "SW00000001",
                "JSONCreationDate": "2025-07-20",
                "IntermediaryCity": "Delhi",
                "Digest": "0000"
            },
            "Form_ITR1": {
                "FormName": "ITR-1",
                "Description": "For Individuals being a Resident (other than NOR) having Total Income up to Rs. 50 lakhs",
                "AssessmentYear": "2025-26",
                "SchemaVer": "Ver1.1",
                "FormVer": "Ver1.1"
            },
            "PersonalInfo": {
                "AssesseeName": {
                    "FirstName": "FIRSTNAME",
                    "SurNameOrOrgName": "SURNAME" 
                },
                "PAN": "ABCDE1234F",
                "AadhaarNo": "123456789012", # Mandatory for AY 2025-26
                "Address": {
                    "ResidenceNo": "123",
                    "LocalityOrArea": "MG ROAD",
                    "CityOrTownOrDistrict": "Delhi",
                    "StateCode": "07",
                    "CountryCode": "91",
                    "MobileNo": 9999999999,
                    "EmailAddress": "test@example.com"
                },
                "DOB": "1990-01-01",
                "EmployerCategory": "OTH",
                "RegimeType": "NEW" # Mandatory: Default is NEW for AY 2025-26
            },
            "FilingStatus": {
                "ReturnFileSec": 1, # Section 139(1) - On or before due date
                "OptOutNewTaxRegime": "N", # Set "Y" only if using Old Regime
                "ItrFilingDueDate": "2025-07-31"
            },
            "ITR1_IncomeDeductions": {
                "GrossSalary": 0,
                "IncomeFromSal": 0,
                "IncomeFromHouseProperty": 0, # Mandatory even if 0
                "IncomeOthSrc": 0,
                "GrossTotIncome": 0,
                "DeductUndChapVIA": {
                    # If claiming, Policy/Document details are now mandatory
                    "Section80C": 0,
                    "Section80D": 0, 
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
                "Section89": 0, 
                "NetTaxLiability": 0,
                "TotalIntrstPay": 0,
                "TotTaxPlusIntrstPay": 0
            },
            "TaxPaid": {
                "TDSonSalary": [], # Detailed arrays mandatory for credits
                "TDSonOthThanSals": [],
                "AdvanceTaxAndSelfAssessmentTax": []
            },
            "Refund": {
                "RefundDue": 0,
                "BankDetail": { # Mandatory for refunds
                    "IFSCCode": "BANK0000123",
                    "BankName": "XYZ BANK",
                    "BankAccountNo": "1234567890"
                }
            },
            "Verification": {
                "Declaration": {
                    "AssesseeName": "FIRSTNAME SURNAME",
                    "FatherName": "FATHER NAME",
                    "Capacity": "S",
                    "Place": "Delhi",
                    "Date": "2025-07-20"
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
                "SWVersionNo": "1.1",
                "SWCreatedBy": "SW00000001",
                "JSONCreatedBy": "SW00000001",
                "JSONCreationDate": "2025-07-20",
                "IntermediaryCity": "Delhi",
                "Digest": "0000"
            },
            "Form_ITR2": {
                "FormName": "ITR-2",
                "Description": "For Individuals and HUFs not having income from profits and gains of business or profession",
                "AssessmentYear": "2025-26",
                "SchemaVer": "Ver1.1",
                "FormVer": "Ver1.1"
            },
            "PartA_GEN1": {
                "PersonalInfo": {
                    "AssesseeName": {
                        "FirstName": "FIRSTNAME",
                        "MiddleName": "",
                        "SurNameOrOrgName": "SURNAME"
                    },
                    "PAN": "ABCDE1234F",
                    "AadhaarNo": "123456789012", # Mandatory for AY 2025-26
                    "Address": {
                        "ResidenceNo": "123",
                        "LocalityOrArea": "MG ROAD",
                        "CityOrTownOrDistrict": "Delhi",
                        "StateCode": "07",
                        "CountryCode": "91",
                        "MobileNo": 9999999999,
                        "EmailAddress": "test@example.com"
                    },
                    "DOB": "1990-01-01",
                    "Status": "I",
                    "RegimeType": "NEW" # Mandatory: Default is NEW for AY 2025-26
                },
                "FilingStatus": {
                    "ReturnFileSec": 1, # Section 139(1) - On or before due date
                    "OptOutNewTaxRegime": "N",
                    "ResidentialStatus": "RES",
                    "ItrFilingDueDate": "2025-07-31"
                }
            },
            "PartB_TI": { # Schema uses underscore here
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
            "PartB_TTI": {
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
            "ScheduleHP": {
                 "IFHP": [] # Structure for each house property entry
            },
            "ScheduleOS": {
                "IncOthSrc": []
            },
            "ScheduleCG": { # Mandatory schedule for ITR2
                "CapGainSummary": {
                    "LTCG10Pct": 0,
                    "LTCG20Pct": 0,
                    "STCG15Pct": 0,
                    "STCGAppRate": 0
                }
            },
            "ScheduleCYLA": {
                 "TotalCurrYrLosses": 0
            },
            "ScheduleBFLA": {
                 "TotalBFLA": 0
            },
             "ScheduleTDS": {
                "TDSonSalaries": [],
                "TDSonOthThanSalaries": []
            },
            "TaxPaid": {
                "TaxesPaid": {
                    "TDSonSalaries": [],
                    "TDSonOthThanSalaries": [],
                    "TCS": [],
                    "AdvanceTaxAndSelfAssessmentTax": []
                }
            },
            "Refund": {
                "RefundDue": 0,
                "BankDetail": { # Mandatory for refunds/validation
                    "IFSCCode": "BANK0000123",
                    "BankName": "XYZ BANK",
                    "BankAccountNo": "1234567890"
                }
            },
            "Verification": {
                "Declaration": {
                    "AssesseeName": "FIRSTNAME SURNAME",
                    "FatherName": "FATHER NAME",
                    "Capacity": "S",
                    "Place": "Delhi",
                    "Date": "2025-07-20"
                }
            }
        }
    }
}
