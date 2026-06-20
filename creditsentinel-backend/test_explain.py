import pandas as pd
import joblib
from app.explain import get_local_explanation

# Simulate a risky profile: low credit score and high debt
mock_application = pd.DataFrame([{
    'credit_score': 450,
    'debt_to_income_ratio': 0.65,
    'credit_utilization_velocity': 0.45,
    'delinquency_multiplier': 4,
    'monthly_income': 3000.0,
    'outstanding_balance_current': 12000.0
}])

calibrated_model = joblib.load("calibrated_xgb_model.joblib")
preprocessor = joblib.load("preprocessor.joblib")

# Calculate prediction probability
X_trans = preprocessor.transform(mock_application)
prob = calibrated_model.predict_proba(X_trans)[0][1]

# Parse drivers
explanation = get_local_explanation(mock_application, prob)

print("\n--- SHAP WATERFALL COMPLIANCE PARSER TEST ---")
print(f"Calculated Default Risk Probability: {explanation['final_risk_probability'] * 100:.2f}%")
print("Top 3 Compliance Decision Drivers:")
for idx, driver in enumerate(explanation['top_decision_drivers'], 1):
    direction = "INCREASING" if driver['shap_value'] > 0 else "DECREASING"
    print(f"{idx}. {driver['feature']} (SHAP Impact: {driver['shap_value']:.4f}) -> {direction} Risk")