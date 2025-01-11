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

"""
Reads in all of the Data files from the relative path, creates a global varible with the dataset
Is makes it so it is only called once when the flask app is started and not every time a user connects

TODO: Write a script to acryously refresh data when new data is expected
"""
def read_and_concatenate_files():
    global df, most_recent
    path = '../../CollectedData'
    all_files = glob.glob(os.path.join(path , "*.csv"))
    for filename in all_files:
        _ = pd.read_csv(filename, index_col=None, header=0)
        li.append(_)
    df = pd.concat(li, axis=0, ignore_index=True)
    df.loc[:, 'Date Issue'] = pd.to_datetime(df['Date Issue'])
    most_recent = df['Date Issue'].max()

read_and_concatenate_files()

"""
Home page that when a user connects a default data is displayed
"""
@app.route('/')
def index():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('index.html', api_key=api_key)

@app.route('/getData', methods=['POST'])
def getData():
    days = request.form.get('days', default=30, type=int)
    ticket_type = request.form.get('type', default='Parking', type=str)

    return jsonify(result = get_UserData(days, ticket_type))


def get_UserData(days, ticket_type):
    global df, most_recent

    localdf = df

    colors = ["#0000e6", "#3b00f2", "#5b00fb", "#7e00fa", "#b500d1", "#d70075", "#e60000"]

    # filters out unneeded data early to make the rest faster
    if (ticket_type is not None and "all" not in ticket_type):
        localdf = localdf[localdf['Type'].str.contains(ticket_type)]

    cutoff_date = most_recent - timedelta(days=days)

    localdf = localdf[(localdf['Date Issue'] >= cutoff_date) & (~localdf['Location'].str.contains("BUCKEYE LOT"))]

    # now starting to look for patterns in the dataset
    # finds most common hour
    grouped_by_hour = localdf.groupby(['Location', 'Type', 'Hour']).size().reset_index(name='Count')
    most_frequent_hours = grouped_by_hour.loc[grouped_by_hour.groupby(['Location', 'Type'])['Count'].idxmax()]
    most_frequent_hours.rename(columns={'Hour': 'Most Frequent Hour', 'Count': 'Max Hour Count'}, inplace=True)

    # finds most common day
    grouped_by_day = localdf.groupby(['Location', 'Type', 'Day']).size().reset_index(name='Count')
    most_frequent_days = grouped_by_day.loc[grouped_by_day.groupby(['Location', 'Type'])['Count'].idxmax()]
    most_frequent_days.rename(columns={'Day': 'Most Frequent Day', 'Count': 'Max Day Count'}, inplace=True)

    # adds to the main dataframe
    localdf = localdf.merge(most_frequent_hours[['Location', 'Type', 'Most Frequent Hour']], on=['Location', 'Type'], how='left')
    localdf = localdf.merge(most_frequent_days[['Location', 'Type', 'Most Frequent Day']], on=['Location', 'Type'], how='left')

    # finds what color each street should be
    # TODO: do this better I am not sure how but better
    df_color = localdf.groupby(['Location', 'Type', 'Most Frequent Hour', 'Most Frequent Day']).size().reset_index(name='Count')
    df_color = df_color.sort_values(by=['Location', 'Count'], ascending=[True, False])
    maxCount = df_color['Count'].max()
    df_color['color'] = df_color.apply(lambda row: colors[round(row['Count'] / maxCount * 6)], axis=1)

    # adds the coordinates to df
    madisonArea = pd.read_csv('../Data/insideMad2.csv', index_col=False)
    madisonArea["Location"] = madisonArea['fullStreetName'].str.upper()
    localdf = df_color.merge(madisonArea, on='Location', how='left').replace({np.nan: None})

    return localdf.to_dict(orient='records')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
