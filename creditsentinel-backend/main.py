import asyncio
import hashlib
import json
import time
import os
import datetime
import pandas as pd
import joblib
import numpy as np
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import redis
from scipy.spatial.distance import euclidean
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.schemas import CreditApplicationCreate
from app.explain import get_local_explanation
from app.database import AsyncSessionLocal
from app.models import ProductionInferenceLog
from monitor_drift import run_drift_analysis

app = FastAPI(title="CreditSentinel Core API Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_STATUS = "HEALTHY"
REQUEST_COUNTER = 0
SEMANTIC_CACHE_REGISTRY = []
DISTANCE_THRESHOLD = 0.05 
PDF_OUTPUT_DIR = "compliance_vault"

os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

try:
    redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

preprocessor = joblib.load("preprocessor.joblib")
calibrated_model = joblib.load("calibrated_xgb_model.joblib")

try:
    challenger_model = joblib.load("challenger_model.joblib")
except Exception:
    challenger_model = None

def run_blocking_inference(df_input):
    X_trans = preprocessor.transform(df_input)
    prob = calibrated_model.predict_proba(X_trans)[0][1]
    explanation = get_local_explanation(df_input, prob)
    return explanation, X_trans

def execute_shadow_evaluation(X_transformed):
    if challenger_model is None:
        return
    try:
        if hasattr(challenger_model, "predict_proba"):
            shadow_prob = challenger_model.predict_proba(X_transformed)[0][1]
        else:
            shadow_prob = 0.0
        print(f"Shadow Run Complete | Challenger Probability: {shadow_prob:.4f}")
    except Exception as e:
        print(f"Shadow Execution Warning: {str(e)}")

def generate_adverse_action_pdf(applicant_name, final_prob, drivers):
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{PDF_OUTPUT_DIR}/AdverseAction_{applicant_name.replace(' ', '_')}_{timestamp_str}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("<b>CREDITSENTINEL COMPLIANCE LEDGER | ADVERSE ACTION NOTICE</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Applicant Name:</b> {applicant_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Evaluation Date:</b> {datetime.datetime.now().isoformat()}", styles["Normal"]))
    story.append(Paragraph(f"<b>Empirical Default Risk Metric:</b> {final_prob:.2%}", styles["Normal"]))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Pursuant to the Fair Credit Reporting Act (FCRA), we regret to inform you that your application for credit extension has been denied based on automated algorithmic underwriting configurations. Below are the primary mathematical attribution vectors driving this decision:", styles["BodyText"]))
    story.append(Spacer(1, 10))
    
    for idx, d in enumerate(drivers, 1):
        item_text = f"<b>Factor {idx}:</b> {d['feature']} (Attribution Impact Score: {d['shap_value']:.4f})"
        story.append(Paragraph(item_text, styles["Normal"]))
        story.append(Spacer(1, 5))
        
    doc.build(story)
    
    with open(filename, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    print(f"Compliance PDF Generated Successfully: {filename} | SHA-256 Ledger Signature: {file_hash}")

@app.post("/api/predict")
async def predict_credit_risk(payload: CreditApplicationCreate, background_tasks: BackgroundTasks):
    global SYSTEM_STATUS, REQUEST_COUNTER, SEMANTIC_CACHE_REGISTRY
    
    dti = payload.monthly_debt / payload.monthly_income
    util_velocity = (payload.outstanding_balance_current - payload.outstanding_balance_prior) / (payload.outstanding_balance_prior + 1e-5)
    del_multiplier = (payload.late_payments_30d * 1) + (payload.late_payments_60d * 2) + (payload.late_payments_90d * 3)
    
    current_vector = np.array([
        float(payload.credit_score) / 850.0,
        float(dti),
        float(util_velocity),
        float(del_multiplier) / 10.0
    ])

    for cached_item in SEMANTIC_CACHE_REGISTRY:
        dist = euclidean(current_vector, cached_item["vector"])
        if dist <= DISTANCE_THRESHOLD:
            return cached_item["payload"]
                
    mock_df = pd.DataFrame([{
        'credit_score': payload.credit_score,
        'debt_to_income_ratio': dti,
        'credit_utilization_velocity': util_velocity,
        'delinquency_multiplier': del_multiplier,
        'monthly_income': payload.monthly_income,
        'outstanding_balance_current': payload.outstanding_balance_current
    }])
    
    loop = asyncio.get_running_loop()
    result, X_trans_array = await loop.run_in_executor(None, run_blocking_inference, mock_df)
    
    background_tasks.add_task(execute_shadow_evaluation, X_trans_array)
    
    # Check if risk profile requires an Adverse Action notice (Denial threshold set to >= 30% default probability)
    if result["final_risk_probability"] >= 0.30:
        background_tasks.add_task(
            generate_adverse_action_pdf, 
            payload.applicant_name, 
            result["final_risk_probability"], 
            result["top_decision_drivers"]
        )
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            log_entry = ProductionInferenceLog(
                credit_score=payload.credit_score,
                debt_to_income_ratio=dti,
                credit_utilization_velocity=util_velocity,
                delinquency_multiplier=del_multiplier,
                monthly_income=payload.monthly_income,
                outstanding_balance_current=payload.outstanding_balance_current,
                predicted_probability=result["final_risk_probability"]
            )
            session.add(log_entry)
            
    REQUEST_COUNTER += 1
    if REQUEST_COUNTER % 10 == 0:
        drift_report = await run_drift_analysis()
        if drift_report["status"] != "INSUFFICIENT_DATA":
            SYSTEM_STATUS = drift_report["status"]

    result["system_status"] = SYSTEM_STATUS
    
    unique_id = f"cache:semantic:{hashlib.md5(str(current_vector).encode('utf-8')).hexdigest()}"
    
    SEMANTIC_CACHE_REGISTRY.append({
        "vector": current_vector,
        "redis_key": unique_id,
        "payload": result
    })
        
    return result

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "system_status": SYSTEM_STATUS, "redis_connected": redis_client is not None}