# ============================================================
# 📄 Unified Tax Form Extraction Pipeline (VS Code-ready)
# ============================================================

import os
from pathlib import Path
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from llama_cloud_services import LlamaExtract
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# ============================================================
# Logging Configuration for form_extraction.py
# ============================================================
def setup_extraction_logger():
    """Set up logging for form extraction to separate log file."""
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "form_extraction.log"
    
    logger = logging.getLogger("form_extraction")
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

extraction_logger = setup_extraction_logger()

# ------------------------------------------------------------
# 🔐 Load environment variables and initialize extractor
# ------------------------------------------------------------
load_dotenv()  # Loads .env file
api_key = os.getenv("LLAMA_CLOUD_API_KEY")
if not api_key:
    raise ValueError("Please set LLAMA_CLOUD_API_KEY in your .env file.")

extractor = LlamaExtract(api_key=api_key)

# ============================================================
# 🧾 FORM SCHEMAS (same as before – kept for completeness)
# ============================================================
# (Keep all your BaseModel classes exactly as defined: Form16PartA, Form16PartB, Form26, AIS, etc.)
# [You don't need to change these — just paste them as-is below the import block]

# [👉 Paste all your class definitions here — EmployerDetailsA, Form16PartA, ..., AIS]

# ============================================================
# 🚀 Extraction Pipeline (modified for local files)
# ============================================================
# ---------- Form 16 Part A ----------
class EmployerDetailsA(BaseModel):
    name: str
    address: str
    PAN: str
    TAN: str
    contact_number: Optional[str]
    email: Optional[str]
 
class EmployeeDetailsA(BaseModel):
    name: str
    address: str
    PAN: str
    employee_reference_no: Optional[str]
 
class AssessmentDetailsA(BaseModel):
    assessment_year: str
    period_from: str
    period_to: str
    CIT_TDS_office: Optional[str]
 
class TDSSummaryItem(BaseModel):
    quarter: str
    tds_receipt_number: str
    amount_paid_credited: float
    tax_deducted: float
    tax_deposited: float
 
class TDSTotals(BaseModel):
    total_amount_paid: float
    total_tax_deducted: float
    total_tax_deposited: float
 
class TaxDepositDetail(BaseModel):
    challan_id: Optional[str]
    bsr_code: str
    date_of_deposit: str
    challan_serial_number: str
    amount_deposited: float
    status: str
 
class CertificateDetails(BaseModel):
    certificate_number: str
    issue_date: str
    place: str
    signatory_name: str
    designation: str
 
class Form16PartA(BaseModel):
    employer_details: EmployerDetailsA
    employee_details: EmployeeDetailsA
    assessment_details: AssessmentDetailsA
    tds_summary: List[TDSSummaryItem]
    tds_totals: TDSTotals
    tax_deposit_details: List[TaxDepositDetail]
    certificate_details: CertificateDetails
 
 
# ---------- Form 16 Part B ----------
class EmployerDetailsB(BaseModel):
    name: str
    address: str
    PAN: str
    TAN: str
    contact_number: str
    email: str
 
class EmployeeDetailsB(BaseModel):
    name: str
    address: str
    PAN: str
 
class AssessmentDetailsB(BaseModel):
    assessment_year: str
    period_from: str
    period_to: str
    CIT_TDS_office: str
 
class SalaryDetails(BaseModel):
    salary_u_s_17_1_a: float
    salary_u_s_17_1_b: float
    salary_u_s_17_3: float
    total_salary: float
    salary_from_other_employers: float
    perquisites_u_s_17_2: float
 
class ExemptionsUS10(BaseModel):
    leave_travel_concession: float
    gratuity: float
    leave_encashment: float
    house_rent_allowance: float
    commuted_pension: float
    any_other_exemption: float
    total_exemptions: float
 
class DeductionsUS16(BaseModel):
    standard_deduction: float
    entertainment_allowance: float
    professional_tax: float
    total_deductions: float
 
class OtherIncomeReported(BaseModel):
    house_property_income: float
    other_sources_income: float
    total_other_income: float
 
class DeductionsChapterVIA(BaseModel):
    section_80C: float
    section_80CCC: float
    section_80CCD_1: float
    section_80CCD_1B: float
    section_80CCD_2: float
    section_80D: float
    section_80E: float
    section_80G: float
    section_80TTA: float
    any_other_deductions: float
    total_deductions: float
 
class TaxComputation(BaseModel):
    income_tax: float
    surcharge: float
    rebate_u_s_87A: float
    health_education_cess: float
    relief_u_s_89: float
    total_tax_liability: float
    tax_deducted_at_source: float
    net_tax_payable_or_refundable: float
 
class Form16PartB(BaseModel):
    employer_details: EmployerDetailsB
    employee_details: EmployeeDetailsB
    assessment_details: AssessmentDetailsB
    salary_details: SalaryDetails
    exemptions_u_s_10: ExemptionsUS10
    net_salary_after_exemptions: float
    deductions_u_s_16: DeductionsUS16
    income_chargeable_under_salary: float
    other_income_reported: OtherIncomeReported
    gross_total_income: float
    deductions_chapter_VIA: DeductionsChapterVIA
    taxable_income: float
    tax_computation: TaxComputation
    certificate_details: CertificateDetails
 
 
# ---------- Form 26 ----------
class AssesseeDetails(BaseModel):
    PAN: str = Field(description="Permanent Account Number of the assessee")
    name: str = Field(description="Name of the assessee")
    address: str = Field(description="Address of the assessee")
    financial_year: str = Field(description="Financial year for the statement (YYYY-YY format)")
    assessment_year: str = Field(description="Assessment year for the statement (YYYY-YY format)")
    pan_status: str = Field(description="Current status of the PAN (e.g., Active)")
 
class Transaction(BaseModel):
    section: str = Field(description="Section under which TDS/TCS was deducted or collected")
    transaction_date: str = Field(description="Date of transaction (YYYY-MM-DD)")
    status_of_booking: Optional[str] = Field(description="Status of booking (F, P, U, O)", default=None)
    date_of_booking: Optional[str] = Field(description="Date of booking (YYYY-MM-DD)", default=None)
    remarks: Optional[str] = Field(description="Remarks, if any", default=None)
    amount_paid: float = Field(description="Amount paid/credited")
    tax_deducted: Optional[float] = Field(description="Tax deducted", default=None)
    tds_deposited: Optional[float] = Field(description="TDS deposited", default=None)
    tax_collected: Optional[float] = Field(description="Tax collected", default=None)
    tcs_deposited: Optional[float] = Field(description="TCS collected", default=None)
 
class DeductorTDS(BaseModel):
    deductor_name: str
    deductor_TAN: str
    total_amount_paid: float
    total_tax_deducted: float
    total_tax_deposited: float
    transactions: List[Transaction]
 
class Deductor15G15H(DeductorTDS):
    pass
 
class DeductorPropertyRentContract(BaseModel):
    acknowledgement_number: str
    deductor_name: str
    deductor_PAN: str
    transaction_date: str
    total_transaction_amount: float
    total_tds_deposited: float
    certificates: List[dict]
 
class CollectorTCS(BaseModel):
    collector_name: str
    collector_TAN: str
    total_amount_paid: float
    total_tax_collected: float
    total_tcs_deposited: float
    transactions: List[Transaction]
 
class TaxPaid(BaseModel):
    major_head: str
    minor_head: str
    tax: float
    surcharge: float
    education_cess: float
    penalty: float
    interest: float
    others: float
    total_tax: float
    bsr_code: str
    date_of_challan: str
    challan_serial_number: str
    remarks: Optional[str] = None
 
class Refund(BaseModel):
    assessment_year: str
    mode: str
    nature_of_refund: str
    refund_amount: float
    interest: float
    date_of_payment: str
    remarks: Optional[str] = None
 
class SFTTransaction(BaseModel):
    transaction_type: str
    sft_filer_name: str
    transaction_date: str
    amount: float
    remarks: Optional[str] = None
 
class BuyerTenantTDS(BaseModel):
    acknowledgement_number: str
    deductee_name: str
    deductee_PAN: str
    transaction_date: str
    total_transaction_amount: float
    total_tds_deposited: float
    total_other_amount_deposited: float
    certificates: List[dict]
 
class TDSDefaults(BaseModel):
    financial_year: str
    short_payment: float
    short_deduction: float
    interest_on_tds_payment: float
    interest_on_tds_deduction: float
    late_filing_fee_234E: float
    interest_220_2: float
    total_default: float
 
class GSTTurnover(BaseModel):
    GSTIN: str
    ARN: str
    date_of_filing: str
    return_period: str
    taxable_turnover: float
    total_turnover: float
 
class Form26(BaseModel):
    assessee_details: AssesseeDetails
    partA_TDS: List[DeductorTDS]
    partA1_TDS_15G_15H: List[Deductor15G15H]
    partA2_TDS_Property_Rent_Contract: List[DeductorPropertyRentContract]
    partB_TCS: List[CollectorTCS]
    partC_Tax_Paid: List[TaxPaid]
    partD_Refunds: List[Refund]
    partE_SFT_Transactions: List[SFTTransaction]
    partF_TDS_Buyer_Tenant: List[BuyerTenantTDS]
    partG_TDS_Defaults: List[TDSDefaults]
    partH_GST_Turnover: List[GSTTurnover]
 
 
# ---------- Form AIS ----------
class AssesseeDetails(BaseModel):
    PAN: str = Field(description="Permanent Account Number of the assessee.")
    name: str = Field(description="Name of the assessee.")
    assessment_year: str = Field(description="Assessment Year for which the statement is.")
    financial_year: str = Field(description="Financial Year for which the statement is.")
 
class TdsTcsInformation(BaseModel):
    source_type: str
    deductor_collector_name: str
    deductor_collector_TAN: str
    income_type: str
    amount_paid_credited: float
    tax_deducted_collected: float
    quarter: Optional[str]
    date_of_transaction: Optional[str]
    remarks: Optional[str]
 
class SftInformation(BaseModel):
    transaction_type: str
    reporting_entity_name: str
    reporting_entity_PAN: str
    transaction_date: str
    transaction_amount: float
    financial_institution_name: Optional[str]
    remarks: Optional[str]
 
class InterestIncome(BaseModel):
    source: str
    bank_or_entity_name: str
    account_number_masked: str
    interest_amount: float
    quarter_or_month: Optional[str]
 
class DividendIncome(BaseModel):
    company_name: str
    isin_code: str
    dividend_amount: float
    date_of_credit: str
    remarks: Optional[str]
 
class SecuritiesTransaction(BaseModel):
    isin_code: str
    script_name: str
    transaction_type: str
    quantity: float
    transaction_value: float
    transaction_date: str
    broker_name: Optional[str]
    exchange: Optional[str]
    remarks: Optional[str]
 
class MutualFundTransaction(BaseModel):
    amc_name: str
    isin_code: str
    scheme_name: str
    transaction_type: str
    units: float
    amount: float
    transaction_date: str
    remarks: Optional[str]
 
class PropertyTransaction(BaseModel):
    property_type: str
    property_address: str
    buyer_seller_name: str
    buyer_seller_PAN: str
    transaction_date: str
    transaction_value: float
    remarks: Optional[str]
 
class ForeignRemittance(BaseModel):
    country: str
    purpose_code: str
    amount_remitted: float
    currency: str
    date_of_remittance: str
    bank_name: str
 
class TaxPaymentInformation(BaseModel):
    bsr_code: str
    date_of_deposit: str
    challan_serial_number: str
    amount: float
    tax_type: str
    remarks: Optional[str]
 
class RefundInformation(BaseModel):
    assessment_year: str
    refund_issue_date: str
    refund_amount: float
    interest_amount: Optional[float]
    mode_of_payment: Optional[str]
    remarks: Optional[str]
 
class FeedbackSummary(BaseModel):
    information_category: str
    reported_value: float
    user_value: float
    feedback_type: str
    final_accepted_value: float
 
# Main AIS schema
class AIS(BaseModel):
    assessee_details: AssesseeDetails
    tds_tcs_information: List[TdsTcsInformation]
    sft_information: List[SftInformation]
    interest_income: List[InterestIncome]
    dividend_income: List[DividendIncome]
    securities_transactions: List[SecuritiesTransaction]
    mutual_fund_transactions: List[MutualFundTransaction]
    property_transactions: List[PropertyTransaction]
    foreign_remittances: List[ForeignRemittance]
    tax_payment_information: List[TaxPaymentInformation]
    refund_information: List[RefundInformation]
    feedback_summary: List[FeedbackSummary]
 




def extract_all_forms():
    """Extract all tax forms using Llama Cloud API and save to data/extracted/"""
    extraction_logger.info("Starting form extraction process...")
    
    # Map filenames in your local directory to schemas
    forms = {
        "Form_16_Part_A.pdf": Form16PartA,
        "Form_16_Part_B.pdf": Form16PartB,
        "Form_26.pdf": Form26,
        "Form_AIS.pdf": AIS,
    }

    # Helper: search a few likely locations for the files so "file not found" is less likely
    REPO_ROOT = Path(__file__).resolve().parents[2]
    search_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parent,  # src/services
        REPO_ROOT,  # project root
        REPO_ROOT / "data",
        REPO_ROOT / "data" / "uploads",
        REPO_ROOT / "data" / "extracted",
        REPO_ROOT / "data" / "templates",
    ]

    def find_file(name: str) -> Optional[str]:
        # Check the exact name first (may be absolute or relative)
        if os.path.exists(name):
            extraction_logger.info(f"Found file: {name}")
            return name
        # Try search dirs
        for d in search_dirs:
            p = d / name
            if p.exists():
                extraction_logger.info(f"Found file in search directories: {p}")
                return str(p)
        # try case-insensitive match in search dirs
        lower = name.lower()
        for d in search_dirs:
            try:
                for entry in d.iterdir():
                    if entry.is_file() and entry.name.lower() == lower:
                        return str(entry)
            except Exception:
                continue
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for file_name, schema in forms.items():
        found = find_file(file_name)
        if not found:
            print(f"⚠️  File not found in searched paths: {file_name}. Skipping.")
            continue

        print(f"\n🔹 Extracting {found} ...")
        agent_name = f"{Path(found).stem}-parser-{timestamp}"

        try:
            agent = extractor.create_agent(name=agent_name, data_schema=schema)
            result = agent.extract(found)  # Pass resolved file path

            # Ensure extracted output is saved under the project's data/extracted directory
            output_dir = REPO_ROOT / "data" / "extracted"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{Path(found).stem}_{timestamp}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result.data, f, indent=4, ensure_ascii=False)

            print(f"✅ Extraction complete → {output_path}")
        except Exception as e:
            print(f"❌ Failed to extract {file_name}: {e}")

def process_uploaded_file(file_path: str, doc_type: str):
    """
    Process a single uploaded file based on its document type.
    """
    extraction_logger.info(f"Processing uploaded file: {file_path} as {doc_type}")
    
    # Map document types to schemas
    # doc_type should be one of: "form16a", "form16b", "form26as", "ais"
    schema_map = {
        "form16a": Form16PartA,
        "form16b": Form16PartB,
        "form26as": Form26,
        "ais": AIS,
    }
    
    schema = schema_map.get(doc_type.lower())
    if not schema:
        raise ValueError(f"Unknown document type: {doc_type}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    agent_name = f"{Path(file_path).stem}-parser-{timestamp}"

    try:
        agent = extractor.create_agent(name=agent_name, data_schema=schema)
        result = agent.extract(file_path)

        # Save extracted output
        REPO_ROOT = Path(__file__).resolve().parents[2]
        output_dir = REPO_ROOT / "data" / "extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{Path(file_path).stem}_{timestamp}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.data, f, indent=4, ensure_ascii=False)

        extraction_logger.info(f"Extraction complete -> {output_path}")
        return result.data

    except Exception as e:
        extraction_logger.error(f"Failed to extract {file_path}: {e}")
        raise e

# ============================================================
# 🧩 Run
# ============================================================
if __name__ == "__main__":
    extract_all_forms()