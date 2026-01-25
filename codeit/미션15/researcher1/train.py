import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 1. Load data
df = pd.read_csv("train.csv")

# 2. 중복 제거
df = df.drop_duplicates()

# 3. Encoding
df['Extracurricular Activities'] = df['Extracurricular Activities'].map({
    'Yes': 1,
    'No': 0
})

# 4. Feature / Target 분리
X = df.drop("Performance Index", axis=1)
y = df["Performance Index"]

# 5. Train / Validation split
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 6. Train model
model = LinearRegression()
model.fit(X_train, y_train)

# 7. Evaluate (RMSE)
y_pred = model.predict(X_val)
# rmse = mean_squared_error(y_val, y_pred, squared=False)# scikit-learn 0.22+ 버전 차이 터짐
rmse = np.sqrt(mean_squared_error(y_val, y_pred))

print(f"RMSE: {rmse:.4f}")

# 8. Save model
# 반드시 /app/output 폴더에 저장해야 함
joblib.dump(model, '/app/output/model.pkl') 
df.to_csv('/app/output/train.csv', index=False)
test = pd.read_csv("test.csv")
test.to_csv('/app/output/test.csv', index=False)