from sqlalchemy import Column, Integer, Float, String, CheckConstraint, DateTime
from app.database import Base
import datetime

class CreditApplication(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_name = Column(String, nullable=False)
    credit_score = Column(Integer, nullable=False)
    monthly_debt = Column(Float, nullable=False)
    monthly_income = Column(Float, nullable=False)
    outstanding_balance_current = Column(Float, nullable=False)
    outstanding_balance_prior = Column(Float, nullable=False)
    late_payments_30d = Column(Integer, default=0)
    late_payments_60d = Column(Integer, default=0)
    late_payments_90d = Column(Integer, default=0)
    risk_label = Column(String, default="LOW")

    __table_args__ = (
        CheckConstraint('credit_score >= 300 AND credit_score <= 850', name='check_credit_score_range'),
        CheckConstraint('monthly_income > 0', name='check_positive_income'),
        CheckConstraint('monthly_debt >= 0', name='check_non_negative_debt'),
    )
    
class ProductionInferenceLog(Base):
    __tablename__ = "production_inference_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    credit_score = Column(Integer, nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)
    credit_utilization_velocity = Column(Float, nullable=False)
    delinquency_multiplier = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    outstanding_balance_current = Column(Float, nullable=False)
    predicted_probability = Column(Float, nullable=False)