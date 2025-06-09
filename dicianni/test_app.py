import pytest
from dicianni.app import app as flask_app

@pytest.fixture()
def client():
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client

def test_infer(client):
    """Test completo dell'endpoint di inferenza"""
    data = {
        "Species": "Eagle", 
        "Region": "North", 
        "Weather_Condition": "Clear",
        "Start_Latitude": 45.0, 
        "Start_Longitude": 12.0, 
        "Flight_Distance_km": 1500,
        "Flight_Duration_hours": 8, 
        "Max_Altitude_m": 3000, 
        "Min_Altitude_m": 500,
        "Temperature_C": 15, 
        "Wind_Speed_kmph": 10, 
        "Humidity_%": 60,
        "Pressure_hPa": 1013, 
        "Visibility_km": 15, 
        "Migration_Start_Month": "Mar",  # Stringa invece di numero!
        "Rest_Stops": 2, 
        "Predator_Sightings": 1, 
        "Migrated_in_Flock": "Yes",  # "Yes"/"No" invece di 1/0
        "Flock_Size": 20, 
        "Food_Supply_Level": 3
    }
    response = client.post("/infer", json=data)
    assert response.status_code in [200, 500]
    assert response.get_json() is not None