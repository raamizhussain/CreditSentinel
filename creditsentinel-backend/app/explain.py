import joblib
import numpy as np
import shap

base_model = joblib.load("base_xgb_model.joblib")
preprocessor = joblib.load("preprocessor.joblib")

explainer = shap.TreeExplainer(base_model)

FEATURE_NAMES = [
    "Credit Score",
    "Debt-to-Income Ratio",
    "Credit Utilization Velocity",
    "Delinquency Multiplier",
    "Monthly Income",
    "Outstanding Balance"
]

def get_local_explanation(raw_features_df, final_probability):
    X_transformed = preprocessor.transform(raw_features_df)
    
    shap_values = explainer.shap_values(X_transformed)
    
    # Extract the array vector for this single inference row
    row_shap = shap_values[0] if isinstance(shap_values, list) else shap_values[0]
    
    # Map raw features to their corresponding SHAP values
    impact_pairs = []
    for i, name in enumerate(FEATURE_NAMES):
        impact_pairs.append({
            "feature": name,
            "shap_value": float(row_shap[i])
        })
        
    # Sort by the absolute impact value to find what shifted the model decision the most
    impact_pairs.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    
    # Isolate top 3 drivers pushing risk boundaries
    top_3_drivers = impact_pairs[:3]
    
    return {
        "final_risk_probability": float(final_probability),
        "top_decision_drivers": top_3_drivers
    }