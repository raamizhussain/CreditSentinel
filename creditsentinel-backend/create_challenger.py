import joblib
from sklearn.linear_model import LogisticRegression

def generate_shadow_challenger():
    dummy_model = LogisticRegression()
    joblib.dump(dummy_model, "challenger_model.joblib")
    print("Shadow Challenger pipeline successfully serialized to challenger_model.joblib")

if __name__ == "__main__":
    generate_shadow_challenger()