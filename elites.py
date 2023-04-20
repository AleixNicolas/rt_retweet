import csv
import json
import os
import logging
import random
import pandas as pd
from twarc import ensure_flattened

logging.getLogger().setLevel(logging.INFO)
TEMPORAL_CSV_PATH = 'output.csv'


def generate_random_file_name():
    return '.' + str(random.randint(0, 20000)) + '_' + TEMPORAL_CSV_PATH


def set_score_value(username, score, dictionary):
    dictionary[username] = score


def get_score_value(username, dictionary):
    return dictionary[username]


def compute_score(username, count, decay, dictionary):
    score = count + decay * get_score_value(username, dictionary) if decay > 0 else count
    set_score_value(username, score, dictionary)
    return score

def main(infile, decay, threshold, granularity, interval, outfile):
    
    decay_granularity = decay
    
    if granularity == 'M':
        decay_granularity= decay**(30)
    if granularity == 'Y':
        decay_granularity= decay**(365.25)
        
    if granularity != 'M' and granularity != 'Y' and granularity != None:
        time_delta = pd.to_timedelta('1'+granularity)
        decay_granularity= decay**(time_delta.total_seconds()/(24*3600)) 
    
    first_temporal_csv = generate_random_file_name()

    f_temp_output = open(first_temporal_csv, 'w', encoding="utf-8")
    f_temp_output.write("created_at,author_name,author_profile\n")

    profile_image_dictionary = dict()
    logging.info('Generating temporal output file: ' + first_temporal_csv)
    is_interval = False

    if interval is not None:
        is_interval = True
        splitted_time = interval.split(',')
        start_time = pd.to_datetime(splitted_time[0], utc=True)
        end_time = pd.to_datetime(splitted_time[1], utc=True)


    # Fill author_profile dictionary and writte date and user in temp_output
    # if in valid period.
    for line in infile:
        for tweet in ensure_flattened(json.loads(line)):
            is_allowed = True
            if 'referenced_tweets' in tweet:
                for x in tweet['referenced_tweets']:
                    if 'retweeted' in x['type']:
                        author_name = x['author']['username']
                        author_profile = x['author']['profile_image_url']
                        created_at = tweet['created_at']
                        profile_image_dictionary[author_name] = author_profile
                        is_allowed = True
                        if is_interval:
                            created_at_time = pd.to_datetime(created_at, utc=True)
                            if not start_time <= created_at_time <= end_time:
                                is_allowed = False
                        if is_allowed:
                            f_temp_output.write("{},{},{}\n".format(created_at, author_name, author_profile))
    f_temp_output.close()

    # Fills list of unique_dates and set of unique authors
    logging.info('Temporal file generated.')
    df = pd.read_csv(first_temporal_csv)
    os.remove(first_temporal_csv)
    if len(df.index) == 0:
        logging.info("No users to process")
        return
    df = df.dropna()
    if granularity is not None:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.to_period(granularity)    
        unique_dates = list(df.created_at.unique())
        unique_dates.sort()
        
    unique_usernames = set(df.author_name.unique())

    dictionary_periods = dict()
    for username in unique_usernames:
        dictionary_periods[username] = 0

    #write temporal file wit profiles and unique dates
    second_temporal_csv = generate_random_file_name()
    f_temp_output = open(second_temporal_csv, 'w', encoding="utf-8")
    f_temp_output.write("profile_image_url,author_name")
    if granularity is not None:
        for unique_date in unique_dates:
            unique_date_str: str = str(unique_date).split('/')[0]
            f_temp_output.write(',' + str(unique_date_str).replace(' ', '_'))
    else:
        f_temp_output.write(',' + str('Accumulated'))    
    f_temp_output.write("\n")


    # Determines score of each user
    logging.info('Computing user scores')
    user_count: int = 1
    total_users: int = len(unique_usernames)
    for user in unique_usernames:
        f_temp_output.write(profile_image_dictionary[user])
        f_temp_output.write(","+user)
        df_filtered_user = df[df['author_name'] == user]
        if granularity is not None:
            for date_period in unique_dates:
                df_filtered = df_filtered_user[df_filtered_user['created_at'] == date_period]
                number_of_rts = len(df_filtered.index)
                score = compute_score(user, number_of_rts, decay_granularity, dictionary_periods)
                f_temp_output.write("," + str(score))
        else: 
            number_of_rts = len(df_filtered_user.index)
            score = compute_score(user, number_of_rts, decay_granularity, dictionary_periods)
            f_temp_output.write("," + str(score))            
        f_temp_output.write("\n")
        logging.info('{}/{}'.format(user_count, total_users))
        user_count = user_count + 1
    f_temp_output.close()

    logging.info('User scores computed. Matrix file generated:' + outfile)
    logging.info('Filtering users...')

    # Write line with username and number of retweets for elites.
    # Elites are users with a number of retweets above threshold
    f_temp_input = open(second_temporal_csv, 'r', encoding="utf-8")
    f_output = open(outfile, 'w', encoding='utf-8')
    csv_file = csv.reader(f_temp_input)
    
    if threshold is None:
        threshold = 0
        number_of_line = 0
        for line in csv_file:
            if number_of_line > 0:
                sum_score = max([float(x) for x in line[2:]])
                threshold = max(threshold, 0.2*sum_score)
            number_of_line += 1
    
    print('Threshold = '+str(threshold))
    
    f_temp_input.seek(0)
    number_of_line = 0 
     
    for line in csv_file:
        if number_of_line > 0:
            sum_score = max([float(x) for x in line[2:]])
            if sum_score >= threshold:
                line_to_write = ','.join(line)
                f_output.write(line_to_write+"\n")
        else:
            f_output.write(','.join(line)+"\n")
        number_of_line += 1

    f_temp_input.close()
    f_output.close()

    os.remove(second_temporal_csv)