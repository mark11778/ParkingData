from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/python-function', methods=['GET'])
def my_python_function():
    data = request.args.get('data', default='default value', type=str)
    # Read CSV data
    df = pd.read_csv('../../../CollectedData/parking_tickets_data_01.csv') 
    df = df.replace({np.nan: None})
    csv_data = df.to_dict(orient='records')
    
    print(f"Python function ran with data: {csv_data}")  # Log to console
    return jsonify({'result': csv_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
