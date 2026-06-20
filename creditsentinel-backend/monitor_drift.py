import asyncio
import numpy as np
import pandas as pd
from sqlalchemy import text
from app.database import AsyncSessionLocal

def calculate_system_drift(expected_distribution, actual_distribution, bucket_count=10):
    breakpoints = np.percentile(expected_distribution, np.linspace(0, 100, bucket_count + 1))
    
    for i in range(1, len(breakpoints)):
        if breakpoints[i] <= breakpoints[i-1]:
            breakpoints[i] = breakpoints[i-1] + 1e-5
            
    expected_percents = np.histogram(expected_distribution, breakpoints)[0] / len(expected_distribution)
    actual_percents = np.histogram(actual_distribution, breakpoints)[0] / len(actual_distribution)
    
    expected_percents = np.where(expected_percents == 0, 1e-4, expected_percents)
    actual_percents = np.where(actual_percents == 0, 1e-4, actual_percents)
    
    psi_metric = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
    return psi_metric

async def run_drift_analysis():
    async with AsyncSessionLocal() as session:
        prod_result = await session.execute(
            text("SELECT credit_score FROM production_inference_logs ORDER BY timestamp DESC LIMIT 500")
        )
        actual_profiles = [row[0] for row in prod_result.fetchall()]

        base_result = await session.execute(text("SELECT credit_score FROM applications"))
        expected_profiles = [row[0] for row in base_result.fetchall()]

    if len(actual_profiles) < 100:
        return {"psi": 0.0, "status": "INSUFFICIENT_DATA"}

    psi_score = calculate_system_drift(expected_profiles, actual_profiles)
    
    status = "HEALTHY"
    if 0.10 <= psi_score < 0.20:
        status = "WARNING"
    elif psi_score >= 0.20:
        status = "DEGRADED"

    return {"psi": psi_score, "status": status}

if __name__ == "__main__":
    res = asyncio.run(run_drift_analysis())
    print(f"Drift Analysis Executed. Result: {res}")