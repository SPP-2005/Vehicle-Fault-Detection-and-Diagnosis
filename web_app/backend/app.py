import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import joblib
import pickle
import os
import traceback

app = Flask(__name__, template_folder='../frontend/templates',
            static_folder='../frontend/static')

MODEL_LOAD_ERROR = None
scaler = detection_model = diagnosis_model = unit_model = severity_model = None
FEATURE_COLUMNS = None
SCALER_COLUMNS = None
MODELS_DIR_PATH = None

def _find_models_dir():
    env = os.environ.get('MODELS_DIR')
    if env and os.path.isdir(env):
        return os.path.abspath(env)

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Models'))
    if os.path.isdir(base):
        return base

    cur = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(cur, 'Models')
        if os.path.isdir(candidate):
            return os.path.abspath(candidate)
        cur = os.path.dirname(cur)

    cand = os.path.join(os.getcwd(), 'Models')
    if os.path.isdir(cand):
        return os.path.abspath(cand)

    return None

def _load_any(path):
    """Try joblib.load, then pickle.load as a fallback. Raises exception if both fail."""
    try:
        return joblib.load(path)
    except Exception:
        with open(path, 'rb') as f:
            return pickle.load(f)

try:
    models_dir = _find_models_dir()
    MODELS_DIR_PATH = models_dir


    if not models_dir:
        MODEL_LOAD_ERROR = (
            "Models directory not found. Place a 'Models' folder in the repo root, or set MODELS_DIR env var to the absolute path."
        )
        print('ERROR:', MODEL_LOAD_ERROR)
    else:
        scaler_path = os.path.join(models_dir, 'scaler.joblib')
        detection_path = os.path.join(models_dir, 'Vehicle_Fault_Detection_Model.pkl')
        diagnosis_path = os.path.join(models_dir, 'Vehicle_Fault_Diagnosis_Model.pkl')
        unit_path = os.path.join(models_dir, 'Vehicle_Fault_Unit_Model.pkl')
        severity_path = os.path.join(models_dir, 'Vehicle_Fault_Severity_Model.pkl')

        required = {
            'scaler.joblib': scaler_path,
            'Vehicle_Fault_Detection_Model.pkl': detection_path,
            'Vehicle_Fault_Diagnosis_Model.pkl': diagnosis_path,
            'Vehicle_Fault_Unit_Model.pkl': unit_path,
            'Vehicle_Fault_Severity_Model.pkl': severity_path,
        }

        missing = [name for name, p in required.items() if not os.path.exists(p)]
        print(f"Looking for models in: {models_dir}")
        for name, p in required.items():
            print(f" - {name}: exists={os.path.exists(p)} path={p}")

        if missing:
            MODEL_LOAD_ERROR = f"Missing model files in Models dir: {missing}"
            try:
                print('Models dir contents:', os.listdir(models_dir))
            except Exception:
                pass
            print('ERROR:', MODEL_LOAD_ERROR)
        else:
            try:
                scaler = _load_any(scaler_path)
                detection_model = _load_any(detection_path)
                diagnosis_model = _load_any(diagnosis_path)
                unit_model = _load_any(unit_path)
                severity_model = _load_any(severity_path)
                print('All models and scaler loaded successfully.')
                try:
                    fc_path = os.path.join(models_dir, 'feature_columns.pkl')
                    if os.path.exists(fc_path):
                        FEATURE_COLUMNS = joblib.load(fc_path)
                        print('Loaded FEATURE_COLUMNS from feature_columns.pkl')
                    else:
                        fcj = os.path.join(models_dir, 'feature_columns.json')
                        if os.path.exists(fcj):
                            import json
                            FEATURE_COLUMNS = json.load(open(fcj))
                            print('Loaded FEATURE_COLUMNS from feature_columns.json')
                except Exception:
                    print('No feature_columns file found or failed to load.')

                try:
                    sc_path = os.path.join(models_dir, 'scaler_columns.pkl')
                    if os.path.exists(sc_path):
                        SCALER_COLUMNS = joblib.load(sc_path)
                        print('Loaded SCALER_COLUMNS from scaler_columns.pkl')
                    else:
                        scj = os.path.join(models_dir, 'scaler_columns.json')
                        if os.path.exists(scj):
                            import json
                            SCALER_COLUMNS = json.load(open(scj))
                            print('Loaded SCALER_COLUMNS from scaler_columns.json')
                except Exception:
                    print('No scaler_columns file found or failed to load.')

                if SCALER_COLUMNS is None:
                    try:
                        sf = getattr(scaler, 'feature_names_in_', None)
                        if sf is None:
                            try:
                                sf = list(scaler.get_feature_names_out())
                            except Exception:
                                sf = None
                        if sf is not None:
                            SCALER_COLUMNS = list(sf)
                            print('Set SCALER_COLUMNS from scaler.feature_names_in_ / get_feature_names_out')
                    except Exception:
                        pass

                if FEATURE_COLUMNS is None:
                    try:
                        fn = getattr(detection_model, 'feature_names_in_', None)
                        if fn is None:
                            fn = getattr(detection_model, 'feature_names_', None)
                        if fn is not None:
                            FEATURE_COLUMNS = list(fn)
                            print('Inferred FEATURE_COLUMNS from detection_model.feature_names_in_')
                    except Exception:
                        pass

                if SCALER_COLUMNS is None:
                    try:
                        n_in = getattr(scaler, 'n_features_in_', None)
                        if n_in is not None and FEATURE_COLUMNS is not None:
                            SCALER_COLUMNS = FEATURE_COLUMNS[:n_in]
                            print('Inferred SCALER_COLUMNS from scaler.n_features_in_ and FEATURE_COLUMNS')
                    except Exception:
                        pass
            except Exception as e:
                MODEL_LOAD_ERROR = f'Exception while loading models: {e}'
                print('ERROR loading models:', MODEL_LOAD_ERROR)
                traceback.print_exc()
except Exception as e:
    MODEL_LOAD_ERROR = f'Unexpected error during model loader initialization: {e}'
    print(MODEL_LOAD_ERROR)
    traceback.print_exc()

FEATURE_ORDER = [
    'Odometer_Reading_km', 'Ambient_Temperature_C', 'Engine_Temp_C',
    'Engine_RPM', 'Oil_Pressure_psi', 'Coolant_Level_pct',
    'Battery_Voltage_V', 'Mass_Airflow_Rate_gs', 'Throttle_Position_pct',
    'Brake_Pad_Wear_pct', 'Tire_Pressure_psi', 'Vibration_Level_mm_s',
    'Fuel_Consumption_L_100km', 'km_per_year', 'temp_difference'
]

@app.route('/')
def home():
    """Renders the main HTML page for the user interface."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles the prediction request from the frontend, runs the ML pipeline,
    and returns the diagnosis.
    """
    


    if not scaler:
        return jsonify({'error': 'Scaler failed to load on the server.'}), 500
    elif not detection_model:
        return jsonify({'error': 'Detection model failed to load on the server.'}), 500
    elif not diagnosis_model:
        return jsonify({'error': 'Diagnosis model failed to load on the server.'}), 500
    elif not unit_model:
        return jsonify({'error': 'Unit model failed to load on the server.'}), 500
    elif not severity_model:
        return jsonify({'error': 'Severity model failed to load on the server.'}), 500
    if FEATURE_COLUMNS is None or SCALER_COLUMNS is None:
        return jsonify({'error': 'Server is missing FEATURE_COLUMNS or SCALER_COLUMNS. Please save feature_columns.pkl and scaler_columns.pkl into the Models folder.'}), 500


    try:
        data = request.get_json(force=True)
        
        vehicle_age = float(data['Vehicle_Age_Years'])
        odometer = float(data['Odometer_Reading_km'])
        
        km_per_year = odometer / vehicle_age if vehicle_age > 0 else 0
        temp_difference = float(data['Engine_Temp_C']) - float(data['Ambient_Temperature_C'])

        features_dict = {
            'Odometer_Reading_km': odometer,
            'Ambient_Temperature_C': float(data['Ambient_Temperature_C']),
            'Engine_Temp_C': float(data['Engine_Temp_C']),
            'Engine_RPM': float(data['Engine_RPM']),
            'Oil_Pressure_psi': float(data['Oil_Pressure_psi']),
            'Coolant_Level_pct': float(data['Coolant_Level_pct']),
            'Battery_Voltage_V': float(data['Battery_Voltage_V']),
            'Mass_Airflow_Rate_gs': float(data['Mass_Airflow_Rate_gs']),
            'Throttle_Position_pct': float(data['Throttle_Position_pct']),
            'Brake_Pad_Wear_pct': float(data['Brake_Pad_Wear_pct']),
            'Tire_Pressure_psi': float(data['Tire_Pressure_psi']),
            'Vibration_Level_mm_s': float(data['Vibration_Level_mm_s']),
            'Fuel_Consumption_L_100km': float(data['Fuel_Consumption_L_100km']),
            'km_per_year': km_per_year,
            'temp_difference': temp_difference
        }

        input_full = {c: 0 for c in FEATURE_COLUMNS}
        for k, v in features_dict.items():
            if k in input_full:
                input_full[k] = v
        brand = data.get('brand') or data.get('Brand') or ''
        if brand:
            col = f'Brand_{str(brand).title()}'
            if col in input_full:
                input_full[col] = 1

        input_df = pd.DataFrame([input_full], columns=FEATURE_COLUMNS)
        expected_scaler_cols = None
        if SCALER_COLUMNS is not None:
            expected_scaler_cols = list(SCALER_COLUMNS)
        else:
            expected_scaler_cols = getattr(scaler, 'feature_names_in_', None)
            if expected_scaler_cols is None:
                try:
                    expected_scaler_cols = list(scaler.get_feature_names_out())
                except Exception:
                    expected_scaler_cols = None

        try:
            if expected_scaler_cols is not None:
                for c in expected_scaler_cols:
                    if c not in input_df.columns:
                        input_df[c] = 0
                input_for_scaler = input_df[expected_scaler_cols]
            else:
                input_for_scaler = input_df.select_dtypes(include=[np.number])

            transformed = scaler.transform(input_for_scaler)
            if expected_scaler_cols is not None:
                input_df[expected_scaler_cols] = transformed
            else:
                num_cols = list(input_for_scaler.columns)
                input_df[num_cols] = transformed

        except Exception as e:
            provided = list(input_df.columns)
            expected = expected_scaler_cols if expected_scaler_cols is not None else getattr(scaler, 'n_features_in_', None)
            print('Scaler transform error:', e)
            print('Provided columns (sample 20):', provided[:20])
            print('Expected scaler columns:', expected)
            traceback.print_exc()
            return jsonify({'error': f'Scaler transform error: {e}', 'provided_columns_sample': provided[:20], 'expected_scaler': expected}), 400

        arr = input_df[FEATURE_COLUMNS].values

        fault_status_prediction = detection_model.predict(arr)
        
        if fault_status_prediction[0] == 0:
            return jsonify({'fault_status': 'No Fault Detected'})
        else:
            fault_type_prediction = diagnosis_model.predict(arr)
            faulty_unit_prediction = unit_model.predict(arr)
            fault_severity_prediction = severity_model.predict(arr)

            severity_score = round(fault_severity_prediction[0])

            return jsonify({
                'fault_status': 'Fault Detected',
                'fault_type': fault_type_prediction[0],
                'faulty_unit': faulty_unit_prediction[0],
                'fault_severity': int(severity_score)
            })

    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return jsonify({'error': f'An error occurred on the server: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/debug_models')
def debug_models():
    """Return JSON diagnostics about loaded models and feature lists."""
    info = {
        'MODEL_LOAD_ERROR': MODEL_LOAD_ERROR,
        'MODELS_DIR': MODELS_DIR_PATH,
        'FEATURE_COLUMNS_len': len(FEATURE_COLUMNS) if FEATURE_COLUMNS is not None else None,
        'SCALER_COLUMNS_len': len(SCALER_COLUMNS) if SCALER_COLUMNS is not None else None,
        'FEATURE_COLUMNS_sample': FEATURE_COLUMNS[:10] if FEATURE_COLUMNS is not None else None,
        'SCALER_COLUMNS_sample': SCALER_COLUMNS[:10] if SCALER_COLUMNS is not None else None,
        'detection_model_n_features_in': getattr(detection_model, 'n_features_in_', None),
        'scaler_n_features_in': getattr(scaler, 'n_features_in_', None),
    }
    return jsonify(info)