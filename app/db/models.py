from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _: Any = None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema()),
                core_schema.no_info_after_validator_function(cls.validate, core_schema.any_schema()),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ---------------------------------------------------------------------------- #
#                                 1. USER SCHEMA                               #
# ---------------------------------------------------------------------------- #

class User(MongoBaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: str
    phone_number: Optional[str] = None
    password_hash: Optional[str] = None
    pan_number: Optional[str] = None
    profile_data: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TokenBlacklist(MongoBaseModel):
    token: str
    blacklisted_on: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------------------------- #
#                                 2. FORM 16 PART A                            #
# ---------------------------------------------------------------------------- #

class EmployerDetailsA(BaseModel):
    name: str
    address: str
    PAN: str
    TAN: str
    contact_number: Optional[str] = None
    email: Optional[str] = None
 
class EmployeeDetailsA(BaseModel):
    name: str
    address: str
    PAN: str
    employee_reference_no: Optional[str] = None
 
class AssessmentDetailsA(BaseModel):
    assessment_year: str
    period_from: str
    period_to: str
    CIT_TDS_office: Optional[str] = None
 
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
    challan_id: Optional[str] = None
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
 
# Base Schema for Extraction (No ID)
class Form16PartA_Schema(BaseModel):
    employer_details: EmployerDetailsA
    employee_details: EmployeeDetailsA
    assessment_details: AssessmentDetailsA
    tds_summary: List[TDSSummaryItem]
    tds_totals: TDSTotals
    tax_deposit_details: List[TaxDepositDetail]
    certificate_details: CertificateDetails

# DB Model
class Form16PartA(Form16PartA_Schema, MongoBaseModel):
    user_id: PyObjectId  # Added link to User
    source_file: str     # Added source tracking
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------- #
#                                 3. FORM 16 PART B                            #
# ---------------------------------------------------------------------------- #

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
 
# Base Schema for Extraction (No ID)
class Form16PartB_Schema(BaseModel):
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

# DB Model
class Form16PartB(Form16PartB_Schema, MongoBaseModel):
    user_id: PyObjectId  # Added link to User
    source_file: str     # Added source tracking
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------- #
#                                 4. AIS                                       #
# ---------------------------------------------------------------------------- #

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
    quarter: Optional[str] = None
    date_of_transaction: Optional[str] = None
    remarks: Optional[str] = None
 
class SftInformation(BaseModel):
    transaction_type: str
    reporting_entity_name: str
    reporting_entity_PAN: str
    transaction_date: str
    transaction_amount: float
    financial_institution_name: Optional[str] = None
    remarks: Optional[str] = None
 
class InterestIncome(BaseModel):
    source: str
    bank_or_entity_name: str
    account_number_masked: str
    interest_amount: float
    quarter_or_month: Optional[str] = None
 
class DividendIncome(BaseModel):
    company_name: str
    isin_code: str
    dividend_amount: float
    date_of_credit: str
    remarks: Optional[str] = None
 
class SecuritiesTransaction(BaseModel):
    isin_code: str
    script_name: str
    transaction_type: str
    quantity: float
    transaction_value: float
    transaction_date: str
    broker_name: Optional[str] = None
    exchange: Optional[str] = None
    remarks: Optional[str] = None
 
class MutualFundTransaction(BaseModel):
    amc_name: str
    isin_code: str
    scheme_name: str
    transaction_type: str
    units: float
    amount: float
    transaction_date: str
    remarks: Optional[str] = None
 
class PropertyTransaction(BaseModel):
    property_type: str
    property_address: str
    buyer_seller_name: str
    buyer_seller_PAN: str
    transaction_date: str
    transaction_value: float
    remarks: Optional[str] = None
 
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
    remarks: Optional[str] = None
 
class RefundInformation(BaseModel):
    assessment_year: str
    refund_issue_date: str
    refund_amount: float
    interest_amount: Optional[float] = None
    mode_of_payment: Optional[str] = None
    remarks: Optional[str] = None
 
class FeedbackSummary(BaseModel):
    information_category: str
    reported_value: float
    user_value: float
    feedback_type: str
    final_accepted_value: float
 
# Main AIS schema
# Base Schema for Extraction
class AIS_Schema(BaseModel):
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

# DB Model
class AIS(AIS_Schema, MongoBaseModel):
    user_id: PyObjectId  # Added link to User
    source_file: str     # Added source tracking
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------- #
#                                 5. ITR SCHEMA                                #
# ---------------------------------------------------------------------------- #

# --- Common ITR Definitions ---
class CreationInfo(BaseModel):
    SWVersionNo: str = "1.0"
    SWCreatedBy: str
    JSONCreatedBy: str
    JSONCreationDate: str
    IntermediaryCity: str = "Delhi"
    Digest: str

class Verification(BaseModel):
    Declaration: Dict[str, Any]
    Capacity: str
    Place: str
    Date: str

# --- ITR-1 Specifics ---
class Form_ITR1(BaseModel):
    FormName: str = "ITR-1"
    Description: str
    AssessmentYear: str = "2025"
    SchemaVer: str = "Ver1.0"
    FormVer: str = "Ver1.0"

class ITR1_IncomeDeductions(BaseModel):
    GrossSalary: int
    Salary: int
    PerquisitesValue: int
    ProfitsInSalary: int
    IncomeNotified89A: int
    NetSalary: int
    DeductionUs16: int
    IncomeFromSal: int
    IncomeOthSrc: int
    GrossTotIncome: int
    TotalIncome: int
    # Allow extra fields for full schema compliance
    class Config:
        extra = "allow"

class ITR1_TaxComputation(BaseModel):
    TotalTaxPayable: int
    Rebate87A: int
    TaxPayableOnRebate: int
    EducationCess: int
    GrossTaxLiability: int
    Section89: int
    NetTaxLiability: int
    TotalIntrstPay: int
    TotTaxPlusIntrstPay: int
    class Config:
        extra = "allow"

class ITR1(BaseModel):
    CreationInfo: CreationInfo
    Form_ITR1: Form_ITR1
    PersonalInfo: Dict[str, Any]
    FilingStatus: Dict[str, Any]
    ITR1_IncomeDeductions: ITR1_IncomeDeductions
    ITR1_TaxComputation: ITR1_TaxComputation
    TaxPaid: Dict[str, Any]
    Refund: Dict[str, Any]
    Verification: Verification
    
    # Optional Schedules
    Schedule80G: Optional[Dict[str, Any]] = None
    Schedule80D: Optional[Dict[str, Any]] = None
    ScheduleTDS1: Optional[Dict[str, Any]] = None
    ScheduleTDS2: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


# --- ITR-2 Specifics ---
class Form_ITR2(BaseModel):
    FormName: str = "ITR-2"
    Description: str
    AssessmentYear: str = "2025"
    SchemaVer: str = "Ver1.0"
    FormVer: str = "Ver1.0"

class ITR2(BaseModel):
    CreationInfo: CreationInfo
    Form_ITR2: Form_ITR2
    PartA_GEN1: Dict[str, Any]
    PartB_TI: Dict[str, Any] = Field(alias="PartB-TI")
    PartB_TTI: Dict[str, Any]
    Verification: Verification
    
    # Schedules
    ScheduleS: Optional[Dict[str, Any]] = None
    ScheduleHP: Optional[Dict[str, Any]] = None
    ScheduleCGFor23: Optional[Dict[str, Any]] = None
    ScheduleOS: Optional[Dict[str, Any]] = None
    ScheduleVIA: Optional[Dict[str, Any]] = None
    Schedule80D: Optional[Dict[str, Any]] = None
    Schedule80G: Optional[Dict[str, Any]] = None
    ScheduleFLA: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"


# --- Main ITR Document ---
class ComputedData(BaseModel):
    total_income: float = 0.0
    total_deductions: float = 0.0
    total_tax_payable: float = 0.0
    regime: str = "OLD"  # OLD or NEW

class ITR(MongoBaseModel):
    user_id: PyObjectId
    assessment_year: str = "2024-25"
    status: str = "DRAFT" # DRAFT, FINAL, FILED
    form_type: str = "ITR-1" # ITR-1 or ITR-2
    
    # Links to source documents
    form16_part_b_ids: List[PyObjectId] = []
    form16_part_a_ids: List[PyObjectId] = []
    ais_ids: List[PyObjectId] = []
    
    computed_data: ComputedData
    
    # The structured ITR data conforming to official schema
    itr_submission: Optional[Dict[str, Any]] = None
    # We use Dict here mainly because Union[ITR1, ITR2] can be tricky with Mongo
    # But ideally, we validate this against ITR1/ITR2 Pydantic models in service layer
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
