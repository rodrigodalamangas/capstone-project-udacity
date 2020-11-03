import pandas as pd
import numpy as np
import math
import json
import time
import sys
from sqlalchemy import create_engine


def clean_portfolio(portfolio_path='data/portfolio.json'):
    """
    Clean Portfolio Dataframe Function

    Arguments:
        portfolio_filepath -> Path to the JSON file containing portfolio data
    Output:
        portfolio -> cleaned portfolio dataframe
    """

    print('Started portfolio dataframe cleaning')
    # read in the json files
    portfolio = pd.read_json(portfolio_path, orient='records', lines=True)
    # divide channels by each type of channel
    portfolio['channel_web'] = portfolio['channels'].apply(
        lambda x: 1 if 'web' in x else 0)
    portfolio['channel_email'] = portfolio['channels'].apply(
        lambda x: 1 if 'email' in x else 0)
    portfolio['channel_mobile'] = portfolio['channels'].apply(
        lambda x: 1 if 'mobile' in x else 0)
    portfolio['channel_social'] = portfolio['channels'].apply(
        lambda x: 1 if 'social' in x else 0)
    # Drop columns channels and offer_type
    portfolio.drop(columns=['channels'], inplace=True)
    # Rename column id for offer_id
    portfolio.rename(columns={'id': 'offer_id'}, inplace=True)
    print('Finished portfolio dataframe cleaning')

    return portfolio


def round_age(x):
    """
    Age Range Function

    Arguments:
    - age
    Output:
    - age range
    """
    for y in range(20, 111, 10):
        if x > y-10 and x <= y:
            return str(y-10) + '-' + str(y)
    return 0


def round_income(x):
    """
    Income Range Function

    Arguments:
    - income
    Output:
    - income range
    """
    for y in range(30, 130, 10):
        if x > (y-10)*1000 and x <= y*1000:
            return str((y-10)*1000) + '-' + str(y*1000)
    return 0


def clean_profile(profile_path='data/profile.json'):
    """
    Clean Profile Dataframe Function

    Arguments:
        profile_path -> Path to the JSON file containing profile data
    Output:
        profile -> cleaned profile dataframe
    """

    print('Started profile dataframe cleaning')
    # read in the json files
    profile = pd.read_json('data/profile.json', orient='records', lines=True)
    # Drop NaN values for gender and income
    profile.dropna(subset=['gender', 'income'], inplace=True)
    # Change to datetime the became_member_on type
    profile['became_member_on'] = pd.to_datetime(
        profile['became_member_on'], format='%Y%m%d')
    # Rename column id for person
    profile.rename(columns={'id': 'person'}, inplace=True)
    # Create age and income range based on their values with round_age and round_income functions
    profile['age_range'] = profile['age'].apply(round_age)
    profile['income_range'] = profile['income'].apply(round_income)
    print('Finished profile dataframe cleaning')

    return profile


def clean_transcript(transcript_path='data/transcript.json'):
    """
    Clean Transcript Dataframe Function

    Arguments:
        transcript_path -> Path to the JSON file containing transcript data
    Output:
        transcript -> cleaned transcript dataframe
    """

    print('Started transcript dataframe cleaning')
    # read in the json files
    transcript = pd.read_json('data/transcript.json',
                              orient='records', lines=True)
    # Create a df that normalize value data into a flat table
    value = pd.json_normalize(transcript['value'])
    # Drop offer id column and join the value df with transcript df
    value.loc[value['offer id'].isnull(
    ) == False, 'offer_id'] = value.loc[value['offer id'].isnull() == False, 'offer id']
    transcript = transcript.join(value).drop(columns=['value', 'offer id'])
    # Drop duplicated rows
    transcript.drop_duplicates(inplace=True)
    # Create dummy variables for column event
    transcript['event'] = transcript['event'].str.replace(' ', '_')
    transcript = transcript.join(pd.get_dummies(
        transcript['event'], prefix='event')).drop(columns='event')
    # Create columns to control offer status
    # Offer received and completed
    transcript['received_and_completed'] = 0
    # Offer completed and viewed
    transcript['completed_and_viewed'] = 0
    # Transactions influenced by offer viewed
    transcript['influenced_transaction'] = 0
    # Transaction return and qty for offer completed calculated with transactions influenced by offer viewed
    transcript['completed_transaction_return'] = 0
    transcript['completed_transaction_qty'] = 0
    print('Creating columns to control offer status, It\'s going to take around 30 min.')
    # Fill in the offer status columns
    start = time.time()
    for person in transcript['person'].unique():

        person_df = transcript[(transcript['person'] == person) & (
            transcript['event_transaction'] == 0)]

        index = np.array(person_df.index)
        offer_id = np.array(person_df.offer_id)
        received = np.array(person_df.event_offer_received)
        viewed = np.array(person_df.event_offer_viewed)
        completed = np.array(person_df.event_offer_completed)

        completed_viewed = []
        completed_viewed_received = []

        for i, x in enumerate(completed):
            pointer = i-1
            if x == 1:
                if pointer >= 0:
                    if viewed[pointer] == 1 and offer_id[pointer] == offer_id[i]:
                        completed_viewed.append([index[i], index[pointer]])
                        if received[pointer-1] == 1 and offer_id[pointer-1] == offer_id[i]:
                            completed_viewed_received.append(
                                [index[i], index[pointer-1]])

        for list_completed in completed_viewed_received:
            transcript.loc[list_completed[1], 'received_and_completed'] = 1

        for list_viewed in completed_viewed:
            transcript.loc[list_viewed[0], 'completed_and_viewed'] = 1
            transcript.loc[list_viewed[1]:list_viewed[0], 'influenced_transaction'][(
                transcript['person'] == person) & (transcript['event_transaction'] == 1)] = 1
            transcript.loc[list_viewed[0], 'completed_transaction_return'] = transcript.loc[list_viewed[1]:list_viewed[0], 'amount'][(
                transcript['person'] == person) & (transcript['event_transaction'] == 1)].sum()
            transcript.loc[list_viewed[0], 'completed_transaction_qty'] = transcript.loc[list_viewed[1]:list_viewed[0], 'amount'][(
                transcript['person'] == person) & (transcript['event_transaction'] == 1)].shape[0]
    print('It took to fill in the offer status columns',
          (time.time() - start)/60, 'minutes.')

    transcript.reward.fillna(0, inplace=True)
    transcript['net_return'] = transcript['completed_transaction_return'] - \
        transcript['reward']
    print('Finished transcript dataframe cleaning')

    return transcript


def merge_dfs(portfolio, profile, transcript):
    """
    Merge Dataframes Function

    Arguments:
        portfolio -> cleaned portfolio dataframe
        profile -> cleaned profile dataframe
        transcript -> cleaned transcript dataframe
    Output:
        df -> Combined data containing all dataframes
    """

    print('Merging Dataframes')
    # Merge using inner for transcript and profile as we are interested in customers characteristics
    df = pd.merge(transcript, profile, on='person', how='inner')
    # Merge using outer for df and portfolio as only offers transcriptions have offer_id
    df = pd.merge(df, portfolio, on='offer_id', how='outer',
                  suffixes=('_transcript', '_portfolio'))

    return df


def save_data(df, database_filename='data/Starbucks.db'):
    """
    Save Data to SQLite Database Function

    Arguments:
        df -> Combined data containing all dataframes
        database_filename -> Path to SQLite destination database
    """

    print('Started saving data in SQLite')
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('df', con=engine, if_exists='replace')
    print('Finished saving data in SQLite')


def main():
    """
    Main function which will kick off the data processing functions. There are three primary actions taken by this function:
        1) Load Dataframes
        2) Clean Dataframes
        3) Save Data to SQLite Database
    """

    portfolio = clean_portfolio()
    profile = clean_profile()
    transcript = clean_transcript()
    df = merge_dfs(portfolio=portfolio, profile=profile, transcript=transcript)
    save_data(df=df)


if __name__ == '__main__':
    main()
