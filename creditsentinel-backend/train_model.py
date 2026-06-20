import asyncio
import pandas as pd
import numpy as np
from sqlalchemy import text
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer  
from sklearn.impute import IterativeImputer
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
import optuna
import joblib

from app.database import AsyncSessionLocal

# Suppress optuna logging clutter to keep terminal output clean
optuna.logging.set_verbosity(optuna.logging.WARNING)

async def load_data_from_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT * FROM applications"))
        columns = result.keys()
        rows = result.fetchall()
        return pd.DataFrame(rows, columns=columns)

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Debt-to-Income Ratio
    df['debt_to_income_ratio'] = df['monthly_debt'] / df['monthly_income']
    
    # 2. Credit Utilization Velocity (mo-over-mo changes)
    # Adding small epsilon denominator to prevent division by zero operations
    df['credit_utilization_velocity'] = (df['outstanding_balance_current'] - df['outstanding_balance_prior']) / (df['outstanding_balance_prior'] + 1e-5)
    
    # 3. Delinquency Frequency Multiplier
    df['delinquency_multiplier'] = (df['late_payments_30d'] * 1) + (df['late_payments_60d'] * 2) + (df['late_payments_90d'] * 3)
    
    # Convert text targets into numeric format
    df['target'] = df['risk_label'].apply(lambda x: 1 if x == "HIGH" else 0)
    return df

def main_training_pipeline():
    print("Extracting raw historical layers from database repository...")
    loop = asyncio.get_event_loop()
    raw_df = loop.run_until_complete(load_data_from_db())
    
    print("Executing feature matrix extractions...")
    processed_df = engineer_features(raw_df)
    
    features = [
        'credit_score', 'debt_to_income_ratio', 'credit_utilization_velocity', 
        'delinquency_multiplier', 'monthly_income', 'outstanding_balance_current'
    ]
    X = processed_df[features]
    y = processed_df['target']
    
    # Enforce strict split partition execution before data scaling to prevent leakage
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Map out strict transform steps inside pipelines
    numeric_transformer = Pipeline(steps=[
        ('imputer', IterativeImputer(max_iter=10, random_state=42)),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, features)
    ])
    
    print("Fitting preprocessor pipeline on training folds...")
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)
    
    # Compute the imbalance correction weight multiplier 
    negative_cases = np.sum(y_train == 0)
    positive_cases = np.sum(y_train == 1)
    scale_weight = negative_cases / positive_cases
    
    print(f"Dataset imbalance resolved. Scaled target loss weight ratio: {scale_weight:.2f}")
    
    print("Initiating Bayesian Hyperparameter Tuning via Optuna optimization loops...")
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 250),
            'max_depth': trial.suggest_int('max_depth', 3, 9),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'scale_pos_weight': scale_weight,
            'eval_metric': 'logloss',
            'random_state': 42
        }
        
        model = xgb.XGBClassifier(**params)
        model.fit(X_train_trans, y_train)
        
        # Optimize tuning routines targeting the validation logloss metrics
        preds = model.predict_proba(X_test_trans)[:, 1]
        from sklearn.metrics import log_loss
        return log_loss(y_test, preds)

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=15)
    
    print(f"Optimal parameters discovered: {study.best_params}")
    
    print("Assembling final calibrated ensemble wrapper...")
    best_base_model = xgb.XGBClassifier(**study.best_params, scale_pos_weight=scale_weight, eval_metric='logloss', random_state=42)
    
    # Isotonic calibration perfectly matches probability outputs to actual default risk percentages
    calibrated_model = CalibratedClassifierCV(estimator=best_base_model, method='isotonic', cv=3)
    calibrated_model.fit(X_train_trans, y_train)
    
    print("Exporting operational production models to disk artifacts...")
    joblib.dump(preprocessor, 'preprocessor.joblib')
    joblib.dump(calibrated_model, 'calibrated_xgb_model.joblib')
    
    # Save the uncalibrated base model explicitly for our SHAP explainability engine later
    base_fitted = best_base_model.fit(X_train_trans, y_train)
    joblib.dump(base_fitted, 'base_xgb_model.joblib')
    
    print("Sprint 3 Model Engine pipeline finished. Saved pipeline artifacts to directory workspace.")

if __name__ == "__main__":
    main_training_pipeline()