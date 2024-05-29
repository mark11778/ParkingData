from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
import os

app = Flask(__name__)
CORS(app)

@app.route('/python-function', methods=['GET'])
def my_python_function():
    data = request.args.get('data', default='default value', type=str)
    
    path = r'C:\Users\marke\projects\parking\ParkingData\scr\CollectedData' # use your path
    all_files = glob.glob(os.path.join(path , "*.csv"))

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)

    df['Date Issue'] = pd.to_datetime(df['Date Issue'])

    days = 30  # will need to be given from the user

    cutoff_date = datetime.now() - timedelta(days=days)

    df = df[df['Date Issue'] >= cutoff_date]


    # should be able to get rid of both of these 
    df['Hour'] = df['Date Issue'].dt.hour
    df['DayOfWeek'] = df['Date Issue'].dt.day_name()

    grouped_by_hour = df.groupby(['Location', 'Type #', 'Hour']).size().reset_index(name='Count')
    most_frequent_hours = grouped_by_hour.loc[grouped_by_hour.groupby(['Location', 'Type #'])['Count'].idxmax()]

    most_frequent_hours.rename(columns={'Hour': 'Most Frequent Hour', 'Count': 'Max Hour Count'}, inplace=True)

    grouped_by_day = df.groupby(['Location', 'Type #', 'DayOfWeek']).size().reset_index(name='Count')

    most_frequent_days = grouped_by_day.loc[grouped_by_day.groupby(['Location', 'Type #'])['Count'].idxmax()]

    most_frequent_days.rename(columns={'DayOfWeek': 'Most Frequent Day', 'Count': 'Max Day Count'}, inplace=True)


    df = df.merge(most_frequent_hours[['Location', 'Type #', 'Most Frequent Hour']], on=['Location', 'Type #'], how='left')
    df = df.merge(most_frequent_days[['Location', 'Type #', 'Most Frequent Day']], on=['Location', 'Type #'], how='left')

    grouped_by_type = df.groupby(['Location', 'Type #', 'Most Frequent Hour', 'Most Frequent Day']).size().reset_index(name='Count')

    grouped_by_type = grouped_by_type.sort_values(by=['Location', 'Count'], ascending=[True, False])

    # Replace NaN values with None
    grouped_by_type = grouped_by_type.replace({np.nan: None})
    csv_data = grouped_by_type.to_dict(orient='records')
    
    print(f"Python function ran with data: {csv_data}")  # Log to console
    return jsonify({'result': csv_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)