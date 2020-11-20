from flask import Flask, request, jsonify, render_template

from app.torch_utils import get_prediction, transform_data, get_ar_data
from datetime import datetime, timedelta
import pandas as pd
import drms
import os

app = Flask(__name__, template_folder='templates', static_url_path='/static')


@app.route('/')
def render_page():
    TAI_time = datetime.utcnow() - timedelta(hours=2)
    TAI_time = TAI_time.strftime('%Y.%m.%d_%H:%M_TAI')
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        # 1 load data
        HARP = int(request.args.get('harp'))
        T_REC = str(request.args.get('time'))
        T_REC = drms.to_datetime(T_REC).strftime('%Y.%m.%d_%H:%M_TAI')
        # T_REC = '$'
        meta_data, input_data = get_ar_data(HARP, T_REC)
        if input_data is None:
            return jsonify({'error': 'No data'})

        try:
            input_tensor = transform_data(input_data)
            prediction = get_prediction(input_tensor)
            data = {'T_REC': meta_data['T_REC'].item(), 'HARP': HARP, 'prediction': prediction.item()}
            return jsonify(data)
        except:
            return jsonify({'error', 'error during prediction'})
    else:
        return jsonify({"error": 'GET or POST is wrong'})

