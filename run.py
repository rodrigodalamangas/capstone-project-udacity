import json
import plotly
import pandas as pd

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar

from sqlalchemy import create_engine

from recommendation_system import load_data, make_recommendation


app = Flask(__name__)


# load data
df = load_data()


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():

    # extract data needed for visuals
    offers_type_x = df[(df['event_offer_received'] == 1)].groupby(
        'offer_type').event_offer_received.sum().sort_values(ascending=False).index
    offers_type_y = df[(df['event_offer_received'] == 1)].groupby(
        'offer_type').event_offer_received.sum().sort_values(ascending=False).values

    offers_x = ['Offers Received', 'Offers Viewed',
                'Offers Viewed and Completed']
    offers_y = [df[(df['event_offer_received'] == 1) & (df['offer_type'] != 'informational')].shape[0],
                df[(df['event_offer_viewed'] == 1) & (
                    df['offer_type'] != 'informational')].shape[0],
                df[(df['completed_and_viewed'] == 1) & (df['offer_type'] != 'informational')].shape[0]]

    transaction_return_x = [
        'Total Transactions', 'Transactions Return (Influenced by offers)', 'Reward Cost', 'Net Return']
    transaction_return_y = [df[df['event_transaction'] == 1].amount.sum().round(2),
                            df[df['completed_and_viewed'] ==
                                1].completed_transaction_return.sum().round(2),
                            df[df['completed_and_viewed'] ==
                                1].reward_transcript.sum().round(2),
                            df[df['completed_and_viewed'] == 1].net_return.sum().round(2)]

    gender_return_x = ['Female', 'Male', 'Other']
    gender_return_y = df[df['completed_and_viewed'] == 1].groupby(
        'gender').net_return.sum().round(2).sort_index().values

    age_return_x = df[df['completed_and_viewed'] == 1].groupby(
        'age_range').net_return.sum().round(2).sort_values(ascending=False).index
    age_return_y = df[df['completed_and_viewed'] == 1].groupby(
        'age_range').net_return.sum().round(2).sort_values(ascending=False).values

    income_return_x = df[df['completed_and_viewed'] == 1].groupby(
        'income_range').net_return.sum().round(2).sort_values(ascending=False).index
    income_return_y = df[df['completed_and_viewed'] == 1].groupby(
        'income_range').net_return.sum().round(2).sort_values(ascending=False).values

    # create visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=offers_type_x,
                    y=offers_type_y,
                    text=offers_type_y,
                    textposition='auto'
                )
            ],

            'layout': {
                'title': 'Offers Type',
                'yaxis': {
                    'title': "Qty"
                },
            }
        },
        {
            'data': [
                Bar(
                    x=offers_x,
                    y=offers_y,
                    text=offers_y,
                    textposition='auto'
                )
            ],

            'layout': {
                'title': 'Offers Received x Viewed x Completed',
                'yaxis': {
                    'title': "Qty"
                },
            }
        },
        {
            'data': [
                Bar(
                    x=transaction_return_x,
                    y=transaction_return_y,
                    text=transaction_return_y,
                    textposition='auto'
                )
            ],

            'layout': {
                'title': 'Total Transactions x Return for completed offers',
                'yaxis': {
                    'title': "$"
                },
            }
        },
        {
            'data': [
                Bar(
                    x=gender_return_x,
                    y=gender_return_y,
                    text=gender_return_y,
                    textposition='auto'
                )
            ],

            'layout': {
                'title': 'Return by gender',
                'yaxis': {
                    'title': "$"
                },
            }
        },
        {
            'data': [
                Bar(
                    x=age_return_x,
                    y=age_return_y,
                    text=age_return_y,
                    textposition='auto'
                )
            ],

            'layout': {
                'title': 'Return by age',
                'yaxis': {
                    'title': "$"
                },
            }
        },
        {
            'data': [
                Bar(
                    x=income_return_x,
                    y=income_return_y,
                    text=income_return_y,
                    textposition='auto'
                )
            ],

            'layout': {
                'title': 'Return by income',
                'yaxis': {
                    'title': "$"
                },
            }
        }
    ]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    gender = request.args.get('gender')
    age = request.args.get('age')
    income = request.args.get('income')

    if not gender:
        gender = None

    if not age:
        age = None

    if not income:
        income = None

    # use model to make recommendation
    offer_list = make_recommendation(
        df=df, gender=gender, age_range=age, income_range=income, n_top=3)

    # This will render the go.html Please see that file.
    return render_template(
        'go.html',
        gender=gender,
        age=age,
        income=income,
        offer_list=offer_list
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
