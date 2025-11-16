from flask import Flask, render_template, request
import pickle, sqlite3, numpy as np, pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Paths
MODEL_PATH = os.path.join('model', 'property_model.pkl')
DB_PATH = 'database.db'

# Load model and encoders
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f'Model not found. Run train_model.py first to create {MODEL_PATH}')

with open(MODEL_PATH, 'rb') as f:
    obj = pickle.load(f)
model = obj['model']
encoders = obj.get('encoders', {})

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  area REAL, bedrooms INTEGER, bathrooms INTEGER, floors INTEGER,
                  year_built INTEGER, location TEXT, condition TEXT, garage TEXT,
                  predicted_price REAL, created_at TEXT)''')
    conn.commit(); conn.close()

init_db()

@app.route('/')
def home():
    # Get unique locations/conditions/garages from dataset (if available) to populate dropdowns
    locs, conds, garages = [], [], []
    data_path = os.path.join('data', 'House Price Prediction Dataset.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        if 'Location' in df.columns:
            locs = sorted(df['Location'].dropna().unique().tolist())
        if 'Condition' in df.columns:
            conds = sorted(df['Condition'].dropna().unique().tolist())
        if 'Garage' in df.columns:
            garages = sorted(df['Garage'].dropna().unique().tolist())
    # fallback defaults
    if not locs:
        locs = ['Downtown','Suburban']
    if not conds:
        conds = ['Excellent','Good','Fair']
    if not garages:
        garages = ['Yes','No']

    return render_template('index.html', locations=locs, conditions=conds, garages=garages)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        area = float(request.form['area'])
        bedrooms = int(request.form['bedrooms'])
        bathrooms = int(request.form['bathrooms'])
        floors = int(request.form['floors'])
        year_built = int(request.form['year_built'])
        location = request.form['location']
        condition = request.form['condition']
        garage = request.form['garage']

        # Encode categorical values using saved encoders (use capitalized keys)
        loc_enc = encoders['Location'].transform([location])[0] if 'Location' in encoders else 0
        cond_enc = encoders['Condition'].transform([condition])[0] if 'Condition' in encoders else 0
        gar_enc = encoders['Garage'].transform([garage])[0] if 'Garage' in encoders else 0

        X = np.array([[area, bedrooms, bathrooms, floors, year_built, loc_enc, cond_enc, gar_enc]])
        price = model.predict(X)[0]

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO predictions(area, bedrooms, bathrooms, floors, year_built, location, condition, garage, predicted_price, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (area, bedrooms, bathrooms, floors, year_built, location, condition, garage, float(price), datetime.now()))
        conn.commit(); conn.close()

        return render_template('result.html', prediction=round(float(price),2), location=location)
    except Exception as e:
        return f"Error during prediction: {e}"

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM predictions', conn)
    conn.close()
    if df.empty:
        labels, values = [], []
    else:
        avg = df.groupby('location')['predicted_price'].mean().reset_index()
        labels = avg['location'].tolist()
        values = avg['predicted_price'].tolist()
    return render_template('dashboard.html', labels=labels, values=values, total=len(df))

if __name__ == '__main__':
    app.run(debug=True)
