# import libraries
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
from etl_pipeline import round_age, round_income


def load_data(database_filepath='data/Starbucks.db'):
    """
    Load Data from the Database Function

    Arguments:
        database_filepath -> Path to SQLite destination database
    Output:
        df -> a dataframe containing cleaned and merged data
    """

    print('Loading Data')
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql('df', con=engine, index_col='index')

    return df


def make_recommendation(df, gender=None, age_range=None, income_range=None, n_top=1):
    """
    Recommendation Engine Function

    Arguments:
        df -> a dataframe containing cleaned and merged data
        gender -> M = Male, F = Female, O = Other
        age_range -> cliente age
        income_range -> cliente anual income
        n_top -> number of top ranked offers
    Output:
        df -> a dataframe containing cleaned and merged data
    """

    df = df[df['completed_and_viewed'] == 1]

    if age_range is not None:
        age_range = round_age(int(age_range))
        if age_range == 0:
            age_range = None

    if income_range is not None:
        income_range = round_income(int(income_range))
        if income_range == 0:
            income_range = None

    if gender is None and age_range is None and income_range is None:
        offer_list = df.groupby(['offer_id'])['net_return'].mean(
        ).sort_values(ascending=False)[:n_top].index
    elif gender is not None and age_range is None and income_range is None:
        offer_list = df[df['gender'] == gender].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index
    elif gender is None and age_range is not None and income_range is None:
        offer_list = df[df['age_range'] == age_range].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index
    elif gender is None and age_range is None and income_range is not None:
        offer_list = df[df['income_range'] == income_range].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index
    elif gender is not None and age_range is not None and income_range is None:
        offer_list = df[(df['gender'] == gender) & (df['age_range'] == age_range)].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index
    elif gender is None and age_range is not None and income_range is not None:
        offer_list = df[(df['age_range'] == age_range) & (df['income_range'] == income_range)].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index
    elif gender is not None and age_range is None and income_range is not None:
        offer_list = df[(df['gender'] == gender) & (df['income_range'] == income_range)].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index
    else:
        offer_list = df[(df['gender'] == gender) & (df['age_range'] == age_range) & (df['income_range'] == income_range)].groupby(
            ['offer_id'])['net_return'].mean().sort_values(ascending=False)[:n_top].index

    return offer_list
