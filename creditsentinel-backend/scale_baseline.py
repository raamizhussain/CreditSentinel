import asyncio
import random
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def scale_enterprise_vault():
    print("Initializing high-speed generation of 125,000 enterprise records...")
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("Seeding 100,000 reference baseline historical records...")
            for i in range(100):
                batch = []
                for _ in range(1000):
                    score = int(random.normalvariate(710, 50))
                    score = max(300, min(850, score))
                    dti = random.uniform(0.15, 0.45)
                    velocity = random.uniform(-0.05, 0.15)
                    mult = random.choice([0, 0, 0, 1, 2])
                    income = random.uniform(4500, 12000)
                    bal = random.uniform(2000, 15000)
                    prob = random.uniform(0.01, 0.25) if score > 680 else random.uniform(0.30, 0.85)
                    
                    batch.append(f"('Enterprise Core', {score}, {dti}, {velocity}, {mult}, {income}, {bal}, {bal-500}, 0, 0, 0, 'LOW')")
                
                values_str = ",".join(batch)
                await session.execute(text(f"INSERT INTO applications (applicant_name, credit_score, debt_to_income_ratio, credit_utilization_velocity, delinquency_multiplier, monthly_income, outstanding_balance_current, outstanding_balance_prior, late_payments_30d, late_payments_60d, late_payments_90d, risk_label) VALUES {values_str}"))
            
            print("Seeding 25,000 streaming production logs...")
            for i in range(25):
                batch = []
                for _ in range(1000):
                    score = int(random.normalvariate(695, 55))
                    score = max(300, min(850, score))
                    dti = random.uniform(0.20, 0.50)
                    velocity = random.uniform(-0.02, 0.20)
                    mult = random.choice([0, 1, 2])
                    income = random.uniform(4000, 11000)
                    bal = random.uniform(3000, 18000)
                    prob = random.uniform(0.05, 0.45)
                    
                    batch.append(f"(NOW() - INTERVAL '{random.randint(1, 30)} DAYS', {score}, {dti}, {velocity}, {mult}, {income}, {bal}, {prob})")
                
                values_str = ",".join(batch)
                await session.execute(text(f"INSERT INTO production_inference_logs (timestamp, credit_score, debt_to_income_ratio, credit_utilization_velocity, delinquency_multiplier, monthly_income, outstanding_balance_current, predicted_probability) VALUES {values_str}"))

    print("Data scaling complete. 125,000 records successfully committed to PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(scale_enterprise_vault())