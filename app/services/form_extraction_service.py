# ============================================================
# 📄 Unified Tax Form Extraction Pipeline (VS Code-ready)
# ============================================================

import os
from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from llama_cloud_services import LlamaExtract
from llama_cloud.types import ExtractConfig
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# ============================================================
# Logging Configuration for form_extraction.py
# ============================================================
def setup_extraction_logger():
    """Set up logging for form extraction to separate log file."""
    log_dir = Path(__file__).resolve().parents[1] / "logs"
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

# Initialize extractor with extended timeouts to handle complex documents
extractor = LlamaExtract(
    api_key=api_key,
    max_timeout=600000,   # 10 minutes (600,000 ms) - Increased for complex AIS files
    httpx_timeout=600.0   # 10 minutes (seconds)
)

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
    """
    Extract all tax forms using Llama Cloud API and save to data/extracted/.
    Discovers files in uploads directory based on doc_type prefixes (form16a_, form16b_, ais_).
    Works with any uploaded filename - no hardcoded file names!
    """
    extraction_logger.info("Starting form extraction process...")
    
    # Map doc_type prefixes to schemas
    doc_type_schemas = {
        "form16a": Form16PartA,
        "form16b": Form16PartB,
        "ais": AIS,
    }

    # Define upload directory
    APP_ROOT = Path(__file__).resolve().parents[1]
    upload_dirs = [
        Path.cwd() / "app" / "data" / "uploads",  # from project root
        APP_ROOT / "data" / "uploads",  # from app root
    ]
    
    # Find the uploads directory that exists
    uploads_dir = None
    for dir_path in upload_dirs:
        if dir_path.exists():
            uploads_dir = dir_path
            extraction_logger.info(f"Using uploads directory: {uploads_dir}")
            break
    
    if not uploads_dir:
        extraction_logger.warning("No uploads directory found")
        raise ValueError("No uploads directory found")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extracted_count = 0

    # Discover and process files for each doc_type
    for doc_type, schema in doc_type_schemas.items():
        # Find files with this doc_type prefix
        matching_files = []
        try:
            for file_path in uploads_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == '.pdf' and file_path.name.startswith(doc_type + "_"):
                    matching_files.append(file_path)
        except Exception as e:
            extraction_logger.error(f"Error listing files in {uploads_dir}: {e}")
            continue
        
        if not matching_files:
            extraction_logger.warning(f"⚠️  No files found with prefix '{doc_type}_' in {uploads_dir}. Skipping.")
            continue
        
        # Process the most recent file for this doc_type
        file_path = max(matching_files, key=lambda p: p.stat().st_mtime)
        extraction_logger.info(f"Processing {doc_type}: {file_path.name}")
        
        try:
            # Create agent and extract
            agent_name = f"{file_path.stem}-{uuid.uuid4().hex}"
            extraction_logger.info(f"Creating agent with name: {agent_name}")
            extraction_logger.info(f"Using schema: {schema.__name__}")
            
            config = ExtractConfig(invalidate_cache=True)
            agent = extractor.create_agent(name=agent_name, data_schema=schema, config=config)
            extraction_logger.info("Agent created successfully with cache invalidation, starting extraction...")
            
            result = agent.extract(str(file_path))
            extraction_logger.info(f"Extraction result type: {type(result)}")
            
            # Parse result
            if hasattr(result, 'data') and result.data:
                extracted_dict = result.data
            else:
                raise ValueError(f"Unexpected result format from LlamaExtract for {file_path.name}")
            
            # Save to extracted directory
            output_dir = APP_ROOT / "data" / "extracted"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{doc_type}_{timestamp}.json"
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(extracted_dict, f, indent=4, ensure_ascii=False)
            
            extraction_logger.info(f"Extraction complete -> {output_path}")
            extracted_count += 1
            
        except Exception as e:
            extraction_logger.error(f"ERROR: Failed to extract {file_path}: {e}")
            continue

    if extracted_count == 0:
        raise ValueError("No tax documents were extracted. Please upload PDF files via the UI (Form 16 Part A, Form 16 Part B, or AIS).")
    
    extraction_logger.info(f"Successfully extracted {extracted_count} document(s)")


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
        "ais": AIS,
    }
    
    schema = schema_map.get(doc_type.lower())
    if not schema:
        raise ValueError(f"Unknown document type: {doc_type}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use full UUID to ensure unique agent name and avoid caching issues
    agent_name = f"{Path(file_path).stem}-{uuid.uuid4().hex}"

    try:
        extraction_logger.info(f"Creating agent with name: {agent_name}")
        extraction_logger.info(f"Using schema: {schema.__name__}")
        
        # Use invalidate_cache=True to bypass Llama Cloud's 48-hour cache
        # This ensures fresh extraction results instead of stale/empty cached data
        config = ExtractConfig(invalidate_cache=True)
        
        agent = extractor.create_agent(name=agent_name, data_schema=schema, config=config)
        extraction_logger.info(f"Agent created successfully with cache invalidation, starting extraction...")
        
        result = agent.extract(file_path)
        
        # Debug logging to identify extraction issues
        extraction_logger.info(f"Extraction result type: {type(result)}")
        extraction_logger.info(f"Result attributes: {dir(result)}")
        extraction_logger.info(f"Result data type: {type(result.data)}")
        extraction_logger.info(f"Result data content: {json.dumps(result.data, indent=2, default=str)[:1000]}...")  # First 1000 chars
        
        # Check for empty values in the result
        if isinstance(result.data, dict):
            empty_keys = [k for k, v in result.data.items() if not v or v == "" or v == [] or v == {}]
            if empty_keys:
                extraction_logger.warning(f"Empty keys in extracted data: {empty_keys}")

        # Save extracted output
        APP_ROOT = Path(__file__).resolve().parents[1]
        output_dir = APP_ROOT / "data" / "extracted"
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