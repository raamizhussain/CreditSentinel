import asyncio
import random
from app.database import AsyncSessionLocal
from app.models import ProductionInferenceLog

async def inject_drifted_population():
    print("Initializing insertion of degraded macroeconomic data profiles...")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for _ in range(150):
                drifted_log = ProductionInferenceLog(
                    credit_score=int(random.normalvariate(480, 40)),
                    debt_to_income_ratio=random.uniform(0.55, 0.85),
                    credit_utilization_velocity=random.uniform(0.20, 0.60),
                    delinquency_multiplier=random.randint(3, 8),
                    monthly_income=random.uniform(2000.0, 3500.0),
                    outstanding_balance_current=random.uniform(15000.0, 30000.0),
                    predicted_probability=random.uniform(0.75, 0.99)
                )
                session.add(drifted_log)
    print("Successfully injected 150 degraded records into PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(inject_drifted_population())