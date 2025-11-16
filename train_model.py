import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
import pickle
import os


DATA_PATH = os.path.join('data', 'House Price Prediction Dataset.csv')
MODEL_DIR = 'model'
MODEL_PATH = os.path.join(MODEL_DIR, 'property_model.pkl')

# Load dataset
print('Loading dataset:', DATA_PATH)
data = pd.read_csv(DATA_PATH)

# Drop Id if present
if 'Id' in data.columns:
    data = data.drop('Id', axis=1)

# Check columns
print('Columns:', data.columns.tolist())

# Fill or handle missing values if any (this dataset had no nulls in preview)
# If there are nulls, fill with median/mode
for col in data.select_dtypes(include=['int64','float64']).columns:
    if data[col].isnull().any():
        data[col] = data[col].fillna(data[col].median())

for col in data.select_dtypes(include=['object']).columns:
    if data[col].isnull().any():
        data[col] = data[col].fillna(data[col].mode()[0])

# Encode categorical features (case-sensitive names from your dataset)
categorical_cols = [c for c in ['Location', 'Condition', 'Garage'] if c in data.columns]
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le

# Define features and target
if 'Price' not in data.columns:
    raise ValueError('Target column "Price" not found in dataset')

X = data.drop('Price', axis=1)
y = data['Price']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Save model and encoders
os.makedirs(MODEL_DIR, exist_ok=True)
with open(MODEL_PATH, 'wb') as f:
    pickle.dump({'model': model, 'encoders': label_encoders}, f)

print('Model trained and saved to', MODEL_PATH)

# Print a small evaluation
# Predict and evaluate
preds = model.predict(X_test)

# Mean Absolute Error
mae = mean_absolute_error(y_test, preds)

# Root Mean Squared Error (manual computation for compatibility)
rmse = np.sqrt(mean_squared_error(y_test, preds))

print(f"Model trained and saved to {MODEL_PATH}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")