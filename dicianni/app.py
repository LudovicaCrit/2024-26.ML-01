from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

def load_model():
    """Carica il modello joblib"""
    return joblib.load('log_reg.joblib')

def make_prediction(model, data):
    """Fa predizione"""
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]
    return {"prediction": int(prediction)}

@app.route('/infer', methods=['POST'])
def infer():
    """Endpoint per inferenza"""
    data = request.get_json()
    
    required_params = [
        'Species', 'Region', 'Weather_Condition', 'Start_Latitude', 
        'Start_Longitude', 'Flight_Distance_km', 'Flight_Duration_hours',
        'Max_Altitude_m', 'Min_Altitude_m', 'Temperature_C', 'Wind_Speed_kmph',
        'Humidity_%', 'Pressure_hPa', 'Visibility_km', 'Migration_Start_Month',
        'Rest_Stops', 'Predator_Sightings', 'Migrated_in_Flock', 
        'Flock_Size', 'Food_Supply_Level'
    ]
    
    missing = [p for p in required_params if p not in data]
    if missing:
        return jsonify({"error": f"Missing: {missing}"}), 400
    
    model = load_model()
    result = make_prediction(model, data)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)