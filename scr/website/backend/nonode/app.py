from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
import os

app = Flask(__name__)
CORS(app)



li = []

# Function to read and concatenate CSV files
def read_and_concatenate_files():
    global ds 
    path = '../../../CollectedData' # use your path
    all_files = glob.glob(os.path.join(path , "*.csv"))
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)
    ds = pd.concat(li, axis=0, ignore_index=True)
    ds.to_csv('test.csv', index=False)

read_and_concatenate_files()


@app.route('/')
def index():
    global ds
    return render_template('index.html')

@app.route('/python-function', methods=['POST'])
def python_function():
    days = request.form.get('days', default=30, type=int)
    ticket_type = request.form.get('type', default='Parking', type=str)

    # Your logic to get data based on `days` and `ticket_type`
    data = get_UserData(days, ticket_type)  # replace this with your actual data fetching logic

    return jsonify(result=data)




def get_UserData(days, ticket_type):
    global ds
    df = ds
    print(df)

    # days = request.args.get('days', default=30, type=int)
    # ticket_type = request.args.get('type', default="Parking", type=str)

    colors = ["#0000e6", "#3b00f2", "#5b00fb", "#7e00fa", "#b500d1", "#d70075", "#e60000"]
    # colors = ["#ff1a1a", "#f25250", "#e47075","#d28899", "#bd9cbb", "#a3addd", "#80bdff"]
    # colors = ['#e60000', '#d70075', '#b500d1', '#7e00fa', '#5b00fb', '#3b00f2', '#0000e6']

    

    if (ticket_type is not None and "all" not in ticket_type):
        df = df[df['Type'].str.contains(ticket_type)]

    # df.loc[:, 'Date Issue'] = pd.to_datetime(df['Date Issue'])
    for index in df.index:
        try:
            df.loc[index, 'Date Issue'] = pd.to_datetime(df.loc[index, 'Date Issue'])
        except Exception as e:
            print(f"Error converting row {df.loc[index]}: {e}")


    cutoff_date = datetime.now() - timedelta(days=days)

    print(df)

    df = df[df['Date Issue'] >= cutoff_date]
    df = df[~df['Location'].str.contains("BUCKEYE LOT")]

    grouped_by_hour = df.groupby(['Location', 'Type', 'Hour']).size().reset_index(name='Count')
    most_frequent_hours = grouped_by_hour.loc[grouped_by_hour.groupby(['Location', 'Type'])['Count'].idxmax()]

    most_frequent_hours.rename(columns={'Hour': 'Most Frequent Hour', 'Count': 'Max Hour Count'}, inplace=True)

    grouped_by_day = df.groupby(['Location', 'Type', 'Day']).size().reset_index(name='Count')

    most_frequent_days = grouped_by_day.loc[grouped_by_day.groupby(['Location', 'Type'])['Count'].idxmax()]


    most_frequent_days.rename(columns={'Day': 'Most Frequent Day', 'Count': 'Max Day Count'}, inplace=True)

    df = df.merge(most_frequent_hours[['Location', 'Type', 'Most Frequent Hour']], on=['Location', 'Type'], how='left')
    df = df.merge(most_frequent_days[['Location', 'Type', 'Most Frequent Day']], on=['Location', 'Type'], how='left')

    grouped_by_type = df.groupby(['Location', 'Type', 'Most Frequent Hour', 'Most Frequent Day']).size().reset_index(name='Count')
    grouped_by_type = grouped_by_type.sort_values(by=['Location', 'Count'], ascending=[True, False])

    maxCount = grouped_by_type['Count'].max()

    print(grouped_by_type)

    # max_count_per_location = grouped_by_type.groupby('Location')['Count'].max().reset_index(name='Max Count')

    # grouped_by_type = grouped_by_type.merge(grouped_by_type, on='Location', how='left')

    grouped_by_type['color'] = grouped_by_type.apply(lambda row: colors[round(row['Count'] / maxCount * 6)], axis=1)
    # for index in df.index:
    #     grouped_by_type.loc[index, 'color'] = colors[round(grouped_by_type.loc[index, 'Count'] / maxCount * 6)]




    temp = pd.read_csv('../Data/insideMad2.csv', index_col=False)
    temp["Location"] = temp['fullStreetName'].str.upper()
    grouped_by_type = grouped_by_type.merge(temp, on='Location', how='left')

    grouped_by_type = grouped_by_type.replace({np.nan: None})
    
    
    csv_data = grouped_by_type.to_dict(orient='records')

    print(f"Python function ran with data: {csv_data}")  # Log to console
    return csv_data
    # return jsonify({'result': csv_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
