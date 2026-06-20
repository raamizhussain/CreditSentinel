import asyncio
import random
from app.database import AsyncSessionLocal
from app.models import CreditApplication
from app.schemas import CreditApplicationCreate

def generate_mock_record(index: int) -> dict:
    income = round(random.uniform(2500, 15000), 2)
    debt = round(random.uniform(200, income * 0.6), 2)
    score = random.randint(300, 850)
    
    current_bal = round(random.uniform(1000, 20000), 2)
    velocity = random.uniform(0.8, 1.4)
    prior_bal = round(current_bal / velocity, 2)
    
    risk = "LOW"
    if score < 580 or (debt / income) > 0.45:
        if random.random() < 0.75:
            risk = "HIGH"
            
    return {
        "applicant_name": f"Applicant_{index}",
        "credit_score": score,
        "monthly_debt": debt,
        "monthly_income": income,
        "outstanding_balance_current": current_bal,
        "outstanding_balance_prior": prior_bal,
        "late_payments_30d": random.choice([0, 0, 0, 1, 2]) if risk == "HIGH" else 0,
        "late_payments_60d": random.choice([0, 0, 0, 1]) if risk == "HIGH" else 0,
        "late_payments_90d": random.choice([0, 0, 1]) if risk == "HIGH" else 0,
        "risk_label": risk
    }

async def stream_chunk_to_db(chunk_data: list):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            db_records = []
            for item in chunk_data:
                validated_data = CreditApplicationCreate(**item)
                db_record = CreditApplication(**validated_data.model_dump())
                db_records.append(db_record)
            session.add_all(db_records)

async def main_ingestion():
    total_records = 5000
    chunk_size = 500
    print(f"Starting ingestion process for {total_records} financial application entries...")
    
    tasks = []
    for i in range(0, total_records, chunk_size):
        chunk = [generate_mock_record(j) for j in range(i, min(i + chunk_size, total_records))]
        tasks.append(stream_chunk_to_db(chunk))
    
    await asyncio.gather(*tasks)
    print("Ingestion complete. Database populated via concurrent async task runners.")

if __name__ == "__main__":
    asyncio.run(main_ingestion())