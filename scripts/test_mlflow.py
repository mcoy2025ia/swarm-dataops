import mlflow
from datetime import datetime

mlflow.set_experiment("test-setup")

with mlflow.start_run(run_name="day3-validation"):
    mlflow.log_param("timestamp", str(datetime.now()))
    mlflow.log_metric("setup_status", 1.0)
    mlflow.log_artifact("README.md")
    print("✅ MLflow logging working")

print("Run recorded. Check http://localhost:5000")
