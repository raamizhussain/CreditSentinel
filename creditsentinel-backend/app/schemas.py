from pydantic import BaseModel, Field

class CreditApplicationCreate(BaseModel):
    applicant_name: str
    credit_score: int = Field(..., ge=300, le=850)
    monthly_debt: float = Field(..., ge=0)
    monthly_income: float = Field(..., gt=0)
    outstanding_balance_current: float = Field(..., ge=0)
    outstanding_balance_prior: float = Field(..., ge=0)
    late_payments_30d: int = Field(0, ge=0)
    late_payments_60d: int = Field(0, ge=0)
    late_payments_90d: int = Field(0, ge=0)
    risk_label: str = Field("LOW")