from flask import Flask, request, jsonify, render_template, make_response, url_for

from app.torch_utils import get_prediction, transform_data, get_ar_data, get_harp_numbers
from datetime import datetime, timedelta
import pandas as pd
import drms
import os
import requests
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__, static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/')
def render_page():
    url_root = request.url_root
    T_REC = datetime.utcnow() - timedelta(hours=2)
    T_REC = T_REC.strftime('%Y.%m.%d_%H:%M_TAI')
    harp_list = get_harp_numbers(T_REC)
    pred_df = pd.DataFrame()
    resp = ['b']
    for harp in harp_list:
        resp = requests.get(f"{url_root}predict?harp={harp}&time={T_REC}").json()
        pred_df = pred_df.append(resp, ignore_index=True)
    print(pred_df)

    if not pred_df.empty:
        df = pred_df.loc[:, ['HARP']]
        df['Probability'] = pred_df["prediction"].apply(lambda x: f'{x*100:.0f} %')
        df['HARP'] = df['HARP'].astype(int)
    else:
        df = pd.DataFrame()

    return render_template('index.html',  tables=[df.to_html(classes='data', header="true")])
    # return pred_df.to_json()


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

# if __name__ == '__main__':
#     app.run(debug=False,port=os.getenv('PORT',5000))
